#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <stdexcept>
#include <cstring>
#include "session.hpp"

static bool
start_subprocess(char *const command[], int *pid, int *infd, int *outfd)
{
    int p1[2], p2[2];

    if (!pid || !infd || !outfd)
        return false;

    if (pipe(p1) == -1)
        goto err_pipe1;
    if (pipe(p2) == -1)
        goto err_pipe2;
    if ((*pid = fork()) == -1)
        goto err_fork;

    if (*pid)
    {
        /* Parent process. */
        *infd = p1[1];
        *outfd = p2[0];
        close(p1[0]);
        close(p2[1]);
        return true;
    }
    else
    {
        /* Child process. */
        dup2(p1[0], 0);
        dup2(p2[1], 1);
        dup2(p2[1], 2);
        close(p1[0]);
        close(p1[1]);
        close(p2[0]);
        close(p2[1]);
        execvp(*command, command);
        /* Error occured. */
        fprintf(stderr, "error running %s: %s", *command, strerror(errno));
        abort();
    }

err_fork:
    close(p2[1]);
    close(p2[0]);
err_pipe2:
    close(p1[1]);
    close(p1[0]);
err_pipe1:
    return false;
}

InteractiveSession::InteractiveSession(const std::string &executable, const std::string &exit_command)
    : executable_(executable), exit_command_(exit_command), pid_(-1), infd_(-1), outfd_(-1)
{
    char *command[] = {const_cast<char *>(executable.c_str()), nullptr};
    if (!start_subprocess(command, &pid_, &infd_, &outfd_))
    {
        throw std::runtime_error("Failed to start subprocess");
    }
}

InteractiveSession::~InteractiveSession()
{
    close();
}

void InteractiveSession::close()
{
    if (pid_ != -1)
    {
        ::close(infd_);
        ::close(outfd_);
        kill(pid_, SIGKILL);
        waitpid(pid_, nullptr, 0);
        pid_ = -1;
    }
}

std::string InteractiveSession::send(const std::string &command)
{

    if (write(infd_, command.c_str(), command.size()) == -1)
    {
        throw std::runtime_error("Failed to write to subprocess");
    }
    if (write(infd_, "\n", 1) == -1)
    {
        throw std::runtime_error("Failed to write to subprocess");
    }
    std::string end = "echo '__END__COMMAND__OUTPUT__'";
    if (write(infd_, end.c_str(), end.size()) == -1)
    {
        throw std::runtime_error("Failed to write to subprocess");
    }
    if (write(infd_, "\n", 1) == -1)
    {
        throw std::runtime_error("Failed to write to subprocess");
    }


    // Set the outfd to non-blocking mode
    // int flags = fcntl(outfd_, F_GETFL, 0); // Fix the undefined identifier error
    // fcntl(outfd_, F_SETFL, flags | O_NONBLOCK);

    std::string output;
    char buffer[4096];
    ssize_t bytes_read;
    while ((bytes_read = read(outfd_, buffer, sizeof(buffer))) > 0)
    {
        output.append(buffer, bytes_read);
        if (output.find("__END__COMMAND__OUTPUT__") != std::string::npos)
        {
            output.erase(output.find("__END__COMMAND__OUTPUT__"));
            break;
        }
    }

    return output;
}
