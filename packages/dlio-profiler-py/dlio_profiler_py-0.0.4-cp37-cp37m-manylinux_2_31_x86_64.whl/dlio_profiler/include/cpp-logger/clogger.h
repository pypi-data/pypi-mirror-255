#ifdef __cplusplus
extern "C" {
#endif
const int CPP_LOGGER_PRINT = 1;
const int CPP_LOGGER_ERROR = 2;
const int CPP_LOGGER_WARN = 3;
const int CPP_LOGGER_INFO = 4;
const int CPP_LOGGER_DEBUG = 5;
const int CPP_LOGGER_TRACE = 6;
extern void cpp_logger_clog(const int logger_level, const char* name, const char* string,
                 ...);
extern void cpp_logger_clog_level(const int logger_level, const char* name);
#ifdef __cplusplus
}
#endif
