//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_POSIX_H
#define BRAHMA_POSIX_H

#include <unistd.h>

#include <cstdlib>
#include <sys/stat.h>
#include "brahma/interceptor.h"
#include "interface.h"
#include <utime.h>
#include <dirent.h>
#include <stdexcept>
#include <fcntl.h>

namespace brahma {
class POSIX :public Interface {
 private:
  static std::shared_ptr<POSIX> my_instance;

 public:
  static std::shared_ptr<POSIX> get_instance() {
    if (my_instance == nullptr) {
      BRAHMA_LOGINFO("POSIX class not intercepted but used", "");
      my_instance = std::make_shared<POSIX>();
    }
    return my_instance;
  }
  POSIX():Interface(){}
  ~POSIX() {}
  static int set_instance(std::shared_ptr<POSIX> instance_i) {
    if (instance_i != nullptr) {
      my_instance = instance_i;
      return 0;
    } else {
      BRAHMA_LOGERROR("instance_i is not set", "");
      throw std::runtime_error("instance_i is not set");
    }
  }

  virtual int open(const char *pathname, int flags, ...);

  virtual int creat64(const char *path, mode_t mode);

  virtual int open64(const char *path, int flags, ...);

  virtual int close(int fd);

  virtual ssize_t write(int fd, const void *buf, size_t count);

  virtual ssize_t read(int fd, void *buf, size_t count);

  virtual off_t lseek(int fd, off_t offset, int whence);

  virtual off64_t lseek64(int fd, off64_t offset, int whence);

  virtual ssize_t pread(int fd, void *buf, size_t count, off_t offset);

  virtual ssize_t pread64(int fd, void *buf, size_t count, off64_t offset);

  virtual ssize_t pwrite(int fd, const void *buf, size_t count, off64_t offset);

  virtual ssize_t pwrite64(int fd, const void *buf, size_t count,
                           off64_t offset);

  virtual int fsync(int fd);

  virtual int fdatasync(int fd);

  virtual int openat(int dirfd, const char *pathname, int flags, ...);
  virtual void* mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);

  virtual void* mmap64(void *addr, size_t length, int prot, int flags, int fd, off64_t offset);
  virtual int __xstat(int vers, const char *path, struct stat *buf);
  virtual int __xstat64(int vers, const char *path, struct stat64 *buf);
  virtual int __lxstat(int vers, const char *path, struct stat *buf);
  virtual int __lxstat64(int vers, const char *path, struct stat64 *buf);
  virtual int __fxstat(int vers, int fd, struct stat *buf);
  virtual int __fxstat64(int vers, int fd, struct stat64 *buf);
  virtual char* getcwd(char *buf, size_t size);
  virtual int mkdir(const char *pathname, mode_t mode);
  virtual int rmdir(const char *pathname);
  virtual int chdir(const char *path);
  virtual int link(const char *oldpath, const char *newpath);
  virtual int linkat(int fd1, const char *path1, int fd2, const char *path2, int flag);
  virtual int unlink(const char *pathname);
  virtual int symlink(const char *path1, const char *path2);
  virtual int symlinkat(const char *path1, int fd, const char *path2);
  virtual ssize_t readlink(const char *path, char *buf, size_t bufsize);
  virtual ssize_t readlinkat(int fd, const char *path, char *buf, size_t bufsize);
  virtual int rename(const char *oldpath, const char *newpath);
  virtual int chmod(const char *path, mode_t mode);
  virtual int chown(const char *path, uid_t owner, gid_t group);
  virtual int lchown(const char *path, uid_t owner, gid_t group);
  virtual int utime(const char *filename, const utimbuf *buf);
  virtual DIR* opendir(const char *name);
  virtual dirent* readdir(DIR *dir);
  virtual int closedir(DIR *dir);
  virtual void rewinddir(DIR *dir);
  virtual int fcntl(int fd, int cmd, ...);
  virtual int dup(int oldfd);
  virtual int dup2(int oldfd, int newfd);
  virtual int pipe(int pipefd[2]);
  virtual int mkfifo(const char *pathname, mode_t mode);
  virtual mode_t umask(mode_t mask);
  virtual int access(const char *path, int amode);
  virtual int faccessat(int fd, const char *path, int amode, int flag);
  virtual int remove(const char *pathname);
  virtual int truncate(const char *pathname, off_t length);
  virtual int ftruncate(int fd, off_t length);
};

}  // namespace brahma

GOTCHA_MACRO_TYPEDEF_OPEN(open, int, (const char *pathname, int flags, ...),
                     (pathname, flags, mode), flags, brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(creat64, int, (const char *path, mode_t mode),
                     (path, mode), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF_OPEN(open64, int, (const char *path, int flags, ...),
                     (path, flags, mode), flags, brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(close, int, (int fd), (fd), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(write, ssize_t, (int fd, const void *buf, size_t count),
                     (fd, buf, count), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(read, ssize_t, (int fd, void *buf, size_t count),
                     (fd, buf, count), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(lseek, off_t, (int fd, off_t offset, int whence),
                     (fd, offset, whence), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(lseek64, off64_t, (int fd, off64_t offset, int whence),
                     (fd, offset, whence), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(pread, ssize_t,
                     (int fd, void *buf, size_t count, off_t offset),
                     (fd, buf, count, offset), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(pread64, ssize_t,
                     (int fd, void *buf, size_t count, off64_t offset),
                     (fd, buf, count, offset), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(pwrite, ssize_t,
                     (int fd, const void *buf, size_t count, off_t offset),
                     (fd, buf, count, offset), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(pwrite64, ssize_t,
                     (int fd, const void *buf, size_t count, off64_t offset),
                     (fd, buf, count, offset), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(fsync, int, (int fd), (fd), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF(fdatasync, int, (int fd), (fd), brahma::POSIX);

GOTCHA_MACRO_TYPEDEF_OPEN(openat, int, (int dirfd, const char *pathname, int flags, ...), (dirfd, pathname, flags, mode), flags, brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(mmap, void *, (void *addr, size_t length, int prot, int flags, int fd, off_t offset),
                                    (addr, length, prot, flags, fd, offset), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(mmap64, void *, (void *addr, size_t length, int prot, int flags, int fd, off64_t offset),
                                      (addr, length, prot, flags, fd, offset), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__xstat, int, (int vers, const char *path, struct stat *buf), (vers, path, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__xstat64, int, (int vers, const char *path, struct stat64 *buf), (vers, path, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__lxstat, int, (int vers, const char *path, struct stat *buf), (vers, path, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__lxstat64, int, (int vers, const char *path, struct stat64 *buf), (vers, path, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__fxstat, int, (int vers, int fd, struct stat *buf), (vers, fd, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(__fxstat64, int, (int vers, int fd, struct stat64 *buf), (vers, fd, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(getcwd, char*, (char *buf, size_t size),(buf, size), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(mkdir, int, (const char *pathname, mode_t mode), (pathname, mode), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(rmdir, int, (const char *pathname), (pathname), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(chdir, int, (const char *path), (path), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(link, int, (const char *oldpath, const char *newpath), (oldpath, newpath), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(linkat, int, (int fd1, const char *path1, int fd2, const char *path2, int flag), (fd1, path1, fd2, path2, flag), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(unlink, int, (const char *pathname), (pathname), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(symlink, int, (const char *path1, const char *path2), (path1, path2), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(symlinkat, int, (const char *path1, int fd, const char *path2), (path1, fd, path2), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(readlink, ssize_t, (const char *path, char *buf, size_t bufsize), (path, buf, bufsize), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(readlinkat, ssize_t, (int fd, const char *path, char *buf, size_t bufsize), (fd, path, buf, bufsize), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(rename, int, (const char *oldpath, const char *newpath), (oldpath, newpath), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(chmod, int, (const char *path, mode_t mode), (path, mode), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(chown, int, (const char *path, uid_t owner, gid_t group), (path, owner, group), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(lchown, int, (const char *path, uid_t owner, gid_t group), (path, owner, group), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(utime, int, (const char *filename, const utimbuf *buf), (filename, buf), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(opendir, DIR*, (const char *name), (name), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(readdir, struct dirent*, (DIR *dir), (dir), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(closedir, int, (DIR *dir), (dir), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(rewinddir, void, (DIR *dir), (dir), brahma::POSIX);
typedef int(*fcntl_fptr) (int fd, int cmd, ...);
  inline int fcntl_wrapper (int fd, int cmd, ...) {
    if(cmd==F_DUPFD || cmd==F_DUPFD_CLOEXEC || cmd==F_SETFD || cmd==F_SETFL || cmd==F_SETOWN) {            // arg: int
      va_list arg;
      va_start(arg, cmd);
      int val = va_arg(arg, int);
      va_end(arg);
      int v = brahma::POSIX::get_instance()->fcntl(fd, cmd, val);
      return v;
    } else if(cmd==F_GETFD || cmd==F_GETFL || cmd==F_GETOWN) {
      int v = brahma::POSIX::get_instance()->fcntl(fd, cmd);
      return v;
    } else if(cmd==F_SETLK || cmd==F_SETLKW || cmd==F_GETLK) {
      va_list arg;
      va_start(arg, cmd);
      struct flock *lk = va_arg(arg, struct flock*);
      va_end(arg);
      int v = brahma::POSIX::get_instance()->fcntl(fd, cmd, lk);
      return v;
    } else {                        // assume arg: void, cmd==F_GETOWN_EX || cmd==F_SETOWN_EX ||cmd==F_GETSIG || cmd==F_SETSIG)
      int v = brahma::POSIX::get_instance()->fcntl(fd, cmd);
      return v;
    }
  };
  gotcha_wrappee_handle_t get_fcntl_handle();
GOTCHA_MACRO_TYPEDEF(dup, int, (int oldfd), (oldfd), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(dup2, int, (int oldfd, int newfd), (oldfd, newfd), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(pipe, int, (int pipefd[2]), (pipefd), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(mkfifo, int, (const char *pathname, mode_t mode), (pathname, mode), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(umask, mode_t, (mode_t mask), (mask), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(access, int, (const char *path, int amode), (path, amode), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(faccessat, int, (int fd, const char *path, int amode, int flag), (fd, path, amode, flag), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(remove, int, (const char *pathname), (pathname), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(truncate, int, (const char *pathname, off_t length), (pathname, length), brahma::POSIX);
GOTCHA_MACRO_TYPEDEF(ftruncate, int, (int fd, off_t length), (fd, length), brahma::POSIX);
#endif  // BRAHMA_POSIX_H
