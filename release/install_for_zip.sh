# 自动完成 fourier-grx 的全部安装过程
rm -rf $HOME/fourier-grx \
&& latest_zip=$(ls fourier-grx-*.zip 2>/dev/null | sort -V | tail -n 1) \
&& echo "latest_zip: $latest_zip" \
&& if [ -z $latest_zip ]; then echo "No fourier-grx zip file found"; exec bash; fi \
&& unzip $latest_zip -d $HOME/fourier-grx \
&& cd $HOME/fourier-grx \
&& chmod +x setup.sh \
&& ./setup.sh \
&& ./config.sh