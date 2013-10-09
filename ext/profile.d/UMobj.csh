if ( "${path}" !~ */opt/UMobj/bin* ) then
        set path = ( /opt/UMobj/bin $path )
endif
if ( "${manpath}" !~ */opt/UMobj/share/man* ) then
        set manpath = ( /opt/UMobj/share/man $manpath )
endif

