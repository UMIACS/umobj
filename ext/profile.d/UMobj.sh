if ! echo ${PATH} | grep -q /opt/UMobj/bin ; then
        PATH=/opt/UMobj/bin:${PATH}
fi
if ! echo ${MANPATH} | grep -q /opt/UMobj/share/man ; then
        MANPATH=/opt/UMobj/share/man:${MANPATH}
fi
