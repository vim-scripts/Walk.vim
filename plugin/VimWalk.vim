" File:  "VimWalk.vim" Last modified : 2003/10/22 11:05:36 .
" Author: Jean-Christophe Clavier (jcclavier@free.Fr)
" Version: 0.3
"
" This plugin permits to visit a set of directory trees, filter the files with
" a wildcard and apply a VIM command to the files found.
" It is based on the python os.path.walk from where it takes its name
"
" If some informations have to be written in an out file, simply write these
" informations in the "o" register during the VIM command to apply
"
" This plugin is given with an example (WkTest) which writes the first line of
" each visited file in the outfile.
" To launch this command on all the files of a directory tree, simply type :
" :Walk WkTest
"
" Roots directories to visit are written in the "d" register. If you have
"       several trees to visit, the roots must be separated by an '\n'
" Wildcard is written in the "w" register
" The content of register "o" is written in the file which name is written in
"       "f" register
"
" Arguments are passed through registers instead of classical argument passing
" to ease the typing (initialisation can be done with a command called each
" time one want to deal with a particular set of directories)
"
" If no command is provided to Walk, the outfile contains the file list
"
" HOW TO USE THIS PLUGIN
"
" To pass arguments, you can set the values of the registers mentionned
" directly. Then, you can type
" :Walk Command
"
" If you don't want to write directly in the registers, you also have some
" commands to write in the registers :
" :WSetRootDir /the/first/root/directory
"   will write the directory in the "d" register
" :WAddRootDir /another/root/directory
"   will add the directory to the "d" register (preceded by an "\n")
" :WSetWildCard \.txt
"   will write the wildcard provided (here : "\.txt") in the "w" register. The
"   wildcard is to be a python regular expression (which are nearly the same as
"   vim's)
" :WSetOutFile /complete/path/file.txt
"   will write the outfile in the "f" register
" These commands provide autocompletion
"
" Finally, there is another way to launch the walk operation : you can call
" the walk function that way :
" :call Walk(cmd,rootdir,wildcard,outfile)
" All the arguments must be provided (with no completion).
" If the registers are already filled and you don't want to replace their
" values, call the funtion walk with "" in the right place. For example :
" :call Walk(cmd,rootdir,"","")
"
" Note : if you use the windows way of calling directories (with \), you must
" be careful : you have to write
" :call Walk(cmd,'D:\my\root\directory',"wc",'C:\my\directory\myFile.txt')
" or
" :call Walk(cmd,"D:\\my\\root\\directory","wc","C:\\my\\directory\\myFile.txt")
"
" Installation
" Warning : This plugin uses Python.
"   It doesn't seem to like when the VIM command passed uses python either.
"
" It is made of two files : VimWalk.vim et VimWalk.py.
" VimWalk.vim is to be dropped in the plugins directory and VimWalk.py
" in a directory declared in the python path :
" let $PYTHONPATH=$PYTHONPATH . "/MyDirectory/Python"
" in .vimrc
"
" These mapping may be useful to copy the content of the clipboard in the
" wanted register
" map _w let @w=@*
" map _d let @d=@*
" map _f let @f=@*
"
"
" Line continuation used here
let s:cpo_save = &cpo
set cpo&vim


if !exists(':Walk')
    command -complete=command -nargs=? Walk call s:CmdWalk(<f-args>)
endif
if !exists(':WSetRootDir')
    command -complete=dir -nargs=1 WSetRootDir call s:WSetRootDir(<f-args>)
endif
if !exists(':WAddRootDir')
    command -complete=dir -nargs=1 WAddRootDir call s:WAddRootDir(<f-args>)
endif
if !exists(':WSetWildCard')
    command -nargs=1 WSetWildCard call s:WSetWildCard(<f-args>)
endif
if !exists(':WSetOutFile')
    command -complete=file -nargs=1 WSetOutFile call s:WSetOutFile(<f-args>)
endif
if !exists(':WkTest')
    command WkTest call s:WkTest()
endif

function! s:WkTest()
    norm ggV"oy
endfunction

function! s:WSetRootDir(...)
    let @d=a:1
endfunction

function! s:WAddRootDir(...)
    let @D="\n" . a:1
endfunction

function! s:WSetWildCard(...)
    let @w=a:1
endfunction

function! s:WSetOutFile(...)
    let @f=a:1
endfunction

function! Walk(cmd, rootDir, wildCard, outFile)
    " Calls the Python function that visits a directory tree and applies the
    " VIM command passed to the files filtered by the wildcard
    " Roots directories to visit are written in th "d" register. If you have
    "       several trees to visit, the roots must be separated by an '\n'
    " Wildcard is written in the "w" register
    " The content of register "o" is written in the file which name is written in
    "       "f" register

    python from VimWalk import *
    if a:rootDir != ""
        let @d=substitute(a:rootDir,"\\","\\\\","")
    endif
    if a:wildCard != ""
        let @w=a:wildCard
    else
        if @w == ""
            let @w="."
        endif
    endif
    if a:outFile != ""
        let @f=substitute(a:outFile,"\\","\\\\","")
    endif
    split
    python argmt = vim.eval("a:cmd")
    python vw=VimWalk(argmt)
    q
endfunction

function! s:CmdWalk(...)
    if a:0 >= 1
        let s:i = 1
        let s:arg = ""
        while s:i <= a:0
            exe "let s:arg = a:" . s:i
            let s:i = s:i + 1
        endwhile
        call Walk(s:arg,"","","")
    else
        call Walk("","","","")
    endif
endfunction

" restore 'cpo'
let &cpo = s:cpo_save
unlet s:cpo_save

