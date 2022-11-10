exec docker run -it --rm \
-v $HOME:$HOME \
-v $PWD/work:$HOME/work -u "$(id -u)" -w "$(pwd)" \
-v /var/run/docker.sock:/var/run/docker.sock  \
-e DUSER=$USER \
-e DSHELL=$SHELL \
--group-add "$(cat $HOME/.kbsdk.cache)" \
--entrypoint sh \
kbase/kb-sdk