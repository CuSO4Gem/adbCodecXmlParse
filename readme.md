这个脚本将自动通过adb下载/apex/com.android.media.swcodec/etc/ /etc 和 /vendor/etc里面的xml文件，并解析出相关的media codece，保存在video_codecs.csv和audio_codecs.csv。  
需要python3和pandas

This script will automatically download xml files aboult media codec in the /apex/com.android.media.swcodec/etc/ /etc and /vendor/etc directories through adb. After downloading, it will parsing the xml files and extractor important information.  
need python3 and pandas  
just run main.py!!
