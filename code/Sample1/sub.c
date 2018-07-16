
#include "zhelpers.h"

int main (int argc, char *argv [])
{
    //  Socket to talk to server
    printf ("Collecting updates from weather server…\n");
    void *context = zmq_ctx_new ();
    void *subscriber = zmq_socket (context, ZMQ_SUB);
//    int rc = zmq_bind(subscriber, "ipc://domainsock");
    int rc = zmq_bind(subscriber, "tcp://127.0.0.1:9000");
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
    int num;
    while(1) {
        char *string = s_recv (subscriber);
        index = strstr(string, needle);
        num = atoi(index);

        if (num % 5 == 0)
            printf("%s",string);
        
        free (string);
    }

    zmq_close (subscriber);
    zmq_ctx_destroy (context);
    return 0;
}
