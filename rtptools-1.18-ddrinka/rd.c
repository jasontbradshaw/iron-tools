#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>  /* struct sockaddr */
#include <netinet/in.h>
#include <arpa/inet.h>   /* inet_ntoa() */
#include <string.h>      /* strncmp() */
#include <sys/time.h>
#include <time.h>        /* localtime() added by Akira 12/27/01 */
#include <unistd.h>      /* usleep() */
#include "types.h"
#include "rtpdump.h"
#define RTPFILE_VERSION "1.0"

/*
* Read header. Return -1 if not valid, 0 if ok.
*/
int RD_header(FILE *in, struct sockaddr_in *sin, int verbose)
{
  RD_hdr_t hdr;
  char line[80], magic[80];

  if (fgets(line, sizeof(line), in) == NULL) return -1;
  sprintf(magic, "#!rtpplay%s ", RTPFILE_VERSION);
  if (strncmp(line, magic, strlen(magic)) != 0) return -1;
  if (fread((char *)&hdr, sizeof(hdr), 1, in) == 0) return -1;
  hdr.start.tv_sec = ntohl(hdr.start.tv_sec);
  hdr.port         = ntohs(hdr.port);
  if (verbose) {
    struct tm *tm;
    struct in_addr in;

    in.s_addr = hdr.source;
    tm = localtime(&hdr.start.tv_sec);
    strftime(line, sizeof(line), "%C", tm);
    printf("Start:  %s\n", line);
    printf("Source: %s (%d)\n", inet_ntoa(in), hdr.port);
  }
  if (sin && sin->sin_addr.s_addr == 0) {
    sin->sin_addr.s_addr = hdr.source;
    sin->sin_port        = htons(hdr.port);
  }
  return 0;
} /* RD_header */


/*
* Read a block of data. If wait_ms_for_succes is set, never fail--continue to try, waiting between attempts.
*/
int RD_do_read(char *buffer, int size, FILE *in, int wait_ms_for_success, int verbose, struct timeval *time_delayed)
{
  int i;

  /* if wait_ms_for_success wasn't set, use fread */
  if(wait_ms_for_success==0) {
    if (fread(buffer, size, 1, in) == 0) {
      return -1;
    }

    return 1;
  }

  /* if wait_ms_for_success was set, use fgetc in a loop */
  for(i=0;i<size;i++) {
    int byte_read;

    do {
      /* attempt to read a byte */
      byte_read=fgetc(in);
      if(byte_read==EOF) {
        /* if reading was unsuccessful */
        if(wait_ms_for_success==0)
          return -1;


        if(verbose)
        {
          printf(".");
          fflush(stdout);
        }
 
        /* wait specified time, clear eof, and try again */
        usleep((useconds_t)(wait_ms_for_success*1000));
        clearerr(in);

        /* track how long we slept to delay plaback the same length of time */
        if(time_delayed!=0) {
          /* XYZZY This introduces a thread-safety issue: if time_delayed is used outsite this routine between
             setting the microseconds and the seconds, it may be nearly a second off or may contain invalid data */
          time_delayed->tv_usec+=wait_ms_for_success*1000;
          while(time_delayed->tv_usec>=1000*1000)
          {
            time_delayed->tv_sec++;
            time_delayed->tv_usec-=1000*1000;
          }
        }
     }
    } while(byte_read==EOF);

    buffer[i]=(char)byte_read;
  }

  return 1;
} /* RD_do_read */


/*
* Read next record from input file.
*/
int RD_read(FILE *in, RD_buffer_t *b, int wait_ms_for_success, int verbose, struct timeval *time_delayed)
{
  /* read packet header from file */
  if (RD_do_read((char *)b->byte, sizeof(b->p.hdr), in, wait_ms_for_success, verbose, time_delayed) == -1) {
    /* we are done */
    return 0;
  }

  /* convert to host byte order */
  b->p.hdr.length = ntohs(b->p.hdr.length) - sizeof(b->p.hdr);
  b->p.hdr.offset = ntohl(b->p.hdr.offset);
  b->p.hdr.plen   = ntohs(b->p.hdr.plen);

  /* read actual packet */
  if (RD_do_read(b->p.data, b->p.hdr.length, in, wait_ms_for_success, verbose, time_delayed) == -1) {
    perror("fread body");
  } 
  return b->p.hdr.length; 
} /* RD_read */
