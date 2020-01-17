<br> Netchron-Juniper-Supporttool (or NJS for short) is a script that helps you to collect all the needed informations for JTAC.</p>
<p class="has-line-data" data-line-start="2" data-line-end="3">I was tired of remembering the needed commands (and probably forgetting some) and the manual time it took me to collect all the Infos.</p>
<p class="has-line-data" data-line-start="4" data-line-end="6">Run this script in python (if you don't trust my .exe) or use the compiled .exe (created via pyinstaller).<br>
The .exe is useful when you don’t have python on your (or your customers) machine.</p>
<p class="has-line-data" data-line-start="7" data-line-end="8">Run it (not as root, but as any user because currently we need direct cli access), give it the Switches IP, user and password and sit back (probably get a coffee or tea).</p>
<p class="has-line-data" data-line-start="9" data-line-end="11">If you have any questions or find bugs feel free to contact me on Twitter (@chsjuniper) <br>or send me a Mail (chs [at] ip4 [dot] de)<br>
This is my first time programming in python - be gentle ;)</p>
<p class="has-line-data" data-line-start="12" data-line-end="13">Simply upload all files in the “configuration”, “core-dump”, “logfiles” and “rsi” folder to JTAC.</p>
<p class="has-line-data" data-line-start="14" data-line-end="15">Do NOT upload the njsupport-live.log - this is for your Info only in case something in the script goes wrong.JTAC will probably not know what to do with that file because it contains almost nothing about your Device ;)</p>
<br>Disclaimer: This Tool is for free use on your own risk. I'm not employed by Juniper - just trying to automate my Tasks ;)
<br>
<br>Currently working on single-devices only (tested on SRX and EX).
<br>For Chassis-Cluster or Virtual-Chassis you need additional commands and that would require some more "discover" tasks to select the correct command for each device-group - but this will definitely be added in the future
<br>Also only working as "non-root" since root is not connected to the cli but the shell which would require an additional command - will also be added in the future.
<br>If you are missing something or have an idea please let me know.
