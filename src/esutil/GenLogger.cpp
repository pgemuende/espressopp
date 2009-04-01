/** \file GenLogger.cpp    Implementation of a genereric Logging facility

<b>Responsible:</b>
<a href="mailto:brandes@scai.fraunhofer.de">Thomas Brandes</a>

*/


#include <iostream>

#include <logging.hpp>
#include <cstdlib>          // import getenv

#include "GenLogger.hpp"

#define DEBUGGING

using namespace log4espp;
using namespace std;

static GenLogger* rootLogger = NULL;

/********************************************************************
*                                                                   *
*  GenLogger also gets its own Logger                               *
*                                                                   *
*    - be careful: do not use it before it has been created         *
*                                                                   *
********************************************************************/

static LOG4ESPP_LOGGER(myLogger, "Logger");

/********************************************************************
*  GenLogger : Constructor                                          *
********************************************************************/

GenLogger::GenLogger(string _name, Logger* _parent) : Logger(_name, _parent)

{
#ifdef DEBUGGING
  printf("GenLogger %s created\n", getFullName().c_str());
#endif
}

/********************************************************************
*  GenLogger :: getRoot                                             *
********************************************************************/

Logger& Logger::getRoot() {

#ifdef DEBUGGING
  printf("getRoot, rootLogger = %p\n");
#endif

  if (rootLogger == NULL) {

     rootLogger = new GenLogger("", NULL);
  }

  return *rootLogger;
}

/********************************************************************
*  GenLogger :: getInstance                                         *
********************************************************************/

Logger& Logger::getInstance (string name) {
  return Logger::createInstance<GenLogger>(name);
}

/********************************************************************
*  GenLogger :: getInstance                                         *
********************************************************************/

static void setLoggerLevel (string& name, string& value) 

{
  Logger::Level level = Logger::WARN;

  if (value == "TRACE") {
     level = Logger::TRACE;
  } else if (value == "DEBUG") {
     level = Logger::DEBUG;
  } else if (value == "INFO") {
     level = Logger::INFO;
  } else if (value == "WARN"){
     level = Logger::WARN;
  } else if (value == "ERROR"){
     level = Logger::ERROR;
  } else if (value == "FATAL") {
     level = Logger::FATAL;
  } else {
    LOG4ESPP_ERROR(myLogger, "logger " << name << " = " << value << ", unknown level");
    return;
  }

  if (name == "root") {
     Logger::getRoot().setLevel(level, true);
  } else {
     Logger::getInstance(name).setLevel(level, true);
  }

  LOG4ESPP_INFO(myLogger, "logger " << name << " = " << value);
}

/********************************************************************
*  GenLogger::traverse                                              *
********************************************************************/

void GenLogger::traverse() 

{ 
  LOG4ESPP_DEBUG(myLogger, "logger " << getFullName() << ", level = " << 
               getLevelString(getEffectiveLevel()) << ", set = " << setFlag);

  for (size_t i = 0; i < sons.size(); i++) {

     GenLogger* son = dynamic_cast<GenLogger*>(sons[i]);
     son->traverse();
  }
}

/********************************************************************
*  help routine: eval_entry                                         *
********************************************************************/

static int eval_entry (char* line, int length, char *filename) 

{
  line[length] = '\0';
 
  string myLine = line;

  // check for an empty line

  string::size_type firstPos = myLine.find_first_not_of(" ", 0);

#ifdef DEBUGGING
  printf("pos of first releveant char = %d\n", firstPos);
#endif

  if (string::npos == firstPos) return 0;

  // check for a comment line

#ifdef DEBUGGING
  printf("first relevant char = %c\n", myLine[firstPos]);
#endif

  if (myLine[firstPos] == '#') return 0;

  // check for an equal sign in the line

  string::size_type equalPos = myLine.find_first_of("=", 0);

  if (string::npos == equalPos) return 0;

  // now find the name without blanks, e.g. "atom vec = " is only atom

  string::size_type lastPos  = myLine.find_first_of(" =", firstPos);
  string name  = myLine.substr(firstPos, lastPos - firstPos);

  firstPos = myLine.find_first_not_of(" ", equalPos+1);
  lastPos  = myLine.find_first_of(" ", firstPos);

#ifdef DEBUGGING
  printf("value at %d - %d\n", firstPos, lastPos);
#endif

  if (string::npos == lastPos) lastPos = myLine.length();
 
  for (int i = firstPos; i <= lastPos; i++) myLine[i] = toupper(myLine[i]);

  string value = myLine.substr(firstPos, lastPos - firstPos);

  setLoggerLevel (name, value);

  return 1;
}

/********************************************************************
*  help routine: read_config for reading a logger configuration     *
********************************************************************/

static int read_config (char *fname)

{ FILE *config_file;

  char buffer [180];
  int  buf_len;
  char c;
  char eof;
  int  no_entries;   /* number of relevant entries */

  config_file = fopen (fname, "r");

  if (config_file == NULL)

    { LOG4ESPP_ERROR(myLogger, "config: could not open config file " << fname);
      return 0;
    }

  buf_len    = 0;
  eof        = EOF;
  no_entries = 0;

  while ((c = fgetc (config_file)) != eof)

    { if (c == '\n')

         { /* new line, evaluate current line */

           no_entries += eval_entry (buffer, buf_len, fname);
           buf_len = 0;
         }

       else buffer [buf_len++] = c;
    }

  if (buf_len > 0)

     no_entries += eval_entry (buffer, buf_len, fname);

  fclose (config_file);

  return no_entries;
}

/********************************************************************
*  Configuration of GenLogger done by reading configuration file    *
********************************************************************/

/*
void Logger::configure()  {

   printf("GenLogger: configure\n");

   getRoot().setLevel(WARN);   // default setting

   char *configFile = getenv("LOG4ESPP"); 

   if (configFile != NULL) {

#ifdef DEBUGGING
      printf("Logger: configFile = %s\n", configFile);
#endif

      LOG4ESPP_INFO(myLogger, "read configuration from file " << configFile);

      read_config(configFile);

   } else { 

#ifdef DEBUGGING
      printf("Logger: LOG4ESPP not set\n");
#endif

      LOG4ESPP_WARN(myLogger, "LOG4ESPP: default configuration"); 
   }  

   GenLogger* root = dynamic_cast<GenLogger*>(&getRoot());

   root->traverse();   // traverse all loggers and might be print it
}
*/

/********************************************************************
*  Helper routine for logging via Python                            *
********************************************************************/

void GenLogger::log(const char* level, Location& loc, const string& msg) 

{  
  printf("%s (%s::%d,func=%s) %s: %s\n", 
          getFullName().c_str(), loc.filename, loc.line, 
          loc.funcname, level, msg.c_str());
}

/********************************************************************
*  Implementation of trace/debug/info/warn/error/fatal              *
********************************************************************/

void GenLogger::trace(Location loc, const string& msg) {

  log("TRACE", loc, msg);
}

void GenLogger::debug(Location loc, const string& msg) {

  log("DEBUG", loc, msg);
}

void GenLogger::info(Location loc, const string& msg) {

  log("INFO", loc, msg);
}

void GenLogger::warn(Location loc, const string& msg) {

  log("WARN", loc, msg);
}

void GenLogger::error(Location loc, const string& msg) {

  log("ERROR", loc, msg);
}

void GenLogger::fatal(Location loc, const string& msg) {
 
  log("FATAL", loc, msg);
}
