FROM ubuntu:latest
LABEL authors="smallziz"

ENTRYPOINT ["top", "-b"]