# Maintainer: Your Name <youremail@domain.com>
pkgname=steal
pkgver=1.1
pkgrel=12
pkgdesc="Free and OpenSource game-center/bittorent client"
arch=(x86_64)
url="https://github.com/AbdelrhmanNile/steal.git"
license=('GPL')
depends=(python python-pip python-kivy python-pandas sharutils fuse-overlayfs xclip zstd npm wine-staging)
makedepends=(git make tcsh)
provides=(steal)
options=()
install=post.install
source=("git+$url")
noextract=()
md5sums=('SKIP')


package() {
	cd steal
	chmod +x build.sh && ./build.sh
	make DESTDIR="$pkgdir/" install
}
