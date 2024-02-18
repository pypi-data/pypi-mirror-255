#include <gtest/gtest.h>
#include "session.hpp"

TEST(InteractiveSessionTest, ExecuteTest)
{
    InteractiveSession session("bash", "exit");
    std::string result = session.send("echo Hello, subprocess!");
    ASSERT_EQ(result, "Hello, subprocess!\n");

    result = session.send("cd /tmp");
    ASSERT_EQ(result, "");
    result = session.send("pwd");
    ASSERT_EQ(result, "/tmp\n");
    result = session.send("ls non_existent_file");
    ASSERT_EQ(result, "ls: non_existent_file: No such file or directory\n");

}


int main(int argc, char **argv)
{
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}