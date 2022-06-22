PREFIX = /usr

all:
	@echo Run \'make install\' to install steal.

install:
	@mkdir -p $(DESTDIR)$(PREFIX)/bin
	@cp -p steal $(DESTDIR)$(PREFIX)/bin/steal
	@chmod 755 $(DESTDIR)$(PREFIX)/bin/steal


uninstall:
	@rm -rf $(DESTDIR)$(PREFIX)/bin/steal
