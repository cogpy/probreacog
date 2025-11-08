#define GIT_SHA1 "0a275a0ea0cce4b05f484725e7edc66ea2167be5"

namespace git
{
const char g_git_sha1[] = GIT_SHA1;

const char *get_sha1()
{
  return g_git_sha1;
}
} // namespace git
