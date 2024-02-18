#ifndef __SESSION_HPP__
#define __SESSION_HPP__
#include <string>

class InteractiveSession
{
public:
  InteractiveSession(const std::string &executable, const std::string &exit_command);
  ~InteractiveSession();
  std::string send(const std::string &command);
  void close();

private:
  std::string executable_;
  std::string exit_command_;

  int pid_;
  int infd_;
  int outfd_;
};
#endif