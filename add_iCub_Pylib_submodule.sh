# config some useful aliases
git config alias.sdiff '!'"git diff && git submodule foreach 'git diff'"
git config alias.spush 'push --recurse-submodules=on-demand'
git config alias.supdate 'submodule update --remote --merge'
git config alias.sinit 'submodule update --init'

if [ $1 == "gogs" ]; then
    echo "Add gogs repository!"
    git submodule add https://ai.informatik.tu-chemnitz.de/gogs/iCub_TUC/iCub_Python_Lib.git  iCub_Python_Lib
elif [ $1 == "github" ]; then
    echo "Add github repository!"
    git submodule add https://github.com/tfietzek/iCub_Python_Lib.git  iCub_Python_Lib
else
    echo "Use this script with parameter \"gogs\" or \"github\"!"
fi
