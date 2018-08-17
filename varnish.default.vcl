vcl 4.0;

backend default {
    .host = "127.0.0.1";
    .port = "8080";
}

sub vcl_recv {
    if (req.url ~ "^/sitestatic/") {
        return (hash);
    } else {
        return (pipe);
    }
}

sub vcl_backend_response {
    if (bereq.url ~ "^/sitestatic/") {
        set beresp.http.Expires = now + 43200s;
	    set beresp.ttl = 720m;
    }
}

sub vcl_deliver {
    unset resp.http.Via;
    unset resp.http.Server;
}
