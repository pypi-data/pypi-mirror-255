//
// Created by hariharan on 8/8/22.
//

#ifndef BRAHMA_STDIO_H
#define BRAHMA_STDIO_H

#include <cstdio>
#include <stdexcept>
#include "interface.h"
#include "brahma/interceptor.h"

namespace brahma {
class STDIO:public Interface {
 private:
  static std::shared_ptr<STDIO> my_instance;

 public:
  static std::shared_ptr<STDIO> get_instance() {
    if (my_instance == nullptr) {
      BRAHMA_LOGINFO("STDIO class not intercepted but used", "");
      my_instance = std::make_shared<STDIO>();
    }
    return my_instance;
  }
  STDIO():Interface(){}
  ~STDIO() {};
  static int set_instance(std::shared_ptr<STDIO> instance_i) {
    if (instance_i != nullptr) {
      my_instance = instance_i;
      return 0;
    } else {
      BRAHMA_LOGERROR("instance_i is not set", "");
      throw std::runtime_error("instance_i is not set");
    }
  }

  virtual FILE *fopen(const char *path, const char *mode);
  virtual FILE *fopen64(const char *path, const char *mode);
  virtual int fclose(FILE *fp);
  virtual size_t fread(void *ptr, size_t size, size_t nmemb, FILE *stream);
  virtual size_t fwrite(const void *ptr, size_t size, size_t nmemb,
                        FILE *stream);
  virtual long ftell(FILE *fp);
  virtual int fseek(FILE *stream, long offset, int whence);
  virtual FILE* fdopen(int fd, const char *mode);
  virtual int fileno(FILE *stream); virtual FILE* tmpfile(void);
  virtual int fseeko(FILE *stream, off_t offset, int whence);
  virtual off_t ftello(FILE *stream);
};

}  // namespace brahma
GOTCHA_MACRO_TYPEDEF(fopen, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(fopen64, FILE *, (const char *path, const char *mode),
                     (path, mode), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(fclose, int, (FILE * fp), (fp), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(fread, size_t,
                     (void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(fwrite, size_t,
                     (const void *ptr, size_t size, size_t nmemb, FILE *stream),
                     (ptr, size, nmemb, stream), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(ftell, long, (FILE * stream), (stream), brahma::STDIO);

GOTCHA_MACRO_TYPEDEF(fseek, int, (FILE * stream, long offset, int whence),
                     (stream, offset, whence), brahma::STDIO);
GOTCHA_MACRO_TYPEDEF(fdopen, FILE*, (int fd, const char *mode), (fd, mode), brahma::STDIO);
GOTCHA_MACRO_TYPEDEF(fileno, int, (FILE *stream), (stream), brahma::STDIO);
GOTCHA_MACRO_TYPEDEF(tmpfile, FILE*, (void), (), brahma::STDIO);
GOTCHA_MACRO_TYPEDEF(fseeko, int, (FILE *stream, off_t offset, int whence), (stream, offset, whence), brahma::STDIO);
GOTCHA_MACRO_TYPEDEF(ftello, off_t, (FILE *stream), (stream), brahma::STDIO);
#endif  // BRAHMA_STDIO_H
