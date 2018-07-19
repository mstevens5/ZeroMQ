//#include "zhelpers.h"
#include <signal.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include <zmq.h>

static char G_Proc_Alive = 1;

void sigint_handler(int arg){
//    G_Proc_Alive = 0;
    printf("hand\n");
    return;
}

char * s_recv(void * sock){
    int chunk = 10;
    char buf[chunk+1];
    int total;
    int count = 1;
    char * msg = NULL;
    while (total > chunk){
        msg = realloc(msg, count * chunk);
        total = zmq_recv(sock, buf, chunk, 0);
        memcpy(msg + ((count-1) * chunk), buf, total);
        count++;
    }
    msg = realloc(msg, (count-1) * chunk + 1);
    msg[(count-1) * chunk] = 0;
    return msg;
}

int main (int argc, char *argv [])
{
    struct sigaction saSigInt;
    //saSigInt.sa_handler = sigint_handler;
    saSigInt.sa_handler = sigint_handler;
    sigemptyset(&saSigInt.sa_mask);
    sigaction(SIGINT, &saSigInt, 0);


    //  Socket to talk to server
    printf ("Collecting updates from weather server…\n");
    void *context = zmq_ctx_new ();
    void *subscriber = zmq_socket (context, ZMQ_SUB);
//    int rc = zmq_bind(subscriber, "ipc://domainsock");
//    int rc = zmq_bind(subscriber, "tcp://127.0.0.1:9000");
    int rc = zmq_connect(subscriber, "tcp://127.0.0.1:9000");
    assert (rc == 0);

    //  Subscribe to zipcode, default is NYC, 10001
    char * accelFilter = "Accel-";
    char * gpsFilter = "GPS-";
    rc = zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE,
                         accelFilter, strlen (accelFilter));
    rc = zmq_setsockopt (subscriber, ZMQ_SUBSCRIBE,
                         gpsFilter, strlen (gpsFilter));
    assert (rc == 0);

    //  Process 100 updates
    int update_nbr;
    long total_temp = 0;
    char * needle = "-";
    char * index;
    int num = 0;
    char * string;
    int rcvMore = 0;
    size_t optLen = sizeof(rcvMore);
    while(G_Proc_Alive) {
        string = s_recv (subscriber);
        if (!string)
            break;
        index = strstr(string, needle);
        index++;
        num = atoi(index);
        
        if (num % 5 == 0)
            printf("%s",string);
        
        free (string);
//        printf("%d\n", num);

    }
    zmq_close (subscriber);
    zmq_ctx_destroy (context);
    return 0;
}
