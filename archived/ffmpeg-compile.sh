set -o errexit

PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH=/usr/local/ffmpeg-compile/build/lib/pkgconfig ./configure \
  --prefix="/usr/local/ffmpeg-compile/build" \
  --extra-cflags="-I/usr/local/ffmpeg-compile/build/include" \
  --extra-ldflags="-L/usr/local/ffmpeg-compile/build/lib" \
  --bindir="/usr/local/ffmpeg-compile/build/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-nonfree \
  --disable-debug \
  --enable-runtime-cpudetect  \
  --enable-libwebp \
  --enable-libspeex \
  --enable-fontconfig \
  --enable-libxvid \
  --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-version3 \
  --enable-libtheora \
  --enable-libvo-amrwbenc \
  --enable-gray \
  --enable-libopenjpeg \
  --enable-gnutls \
  --enable-libvidstab

PATH="$HOME/bin:$PATH" make
make install
make distclean
hash -r
#  --enable-libx265 \
