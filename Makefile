INSTALL = /usr/bin/install
SED = /bin/sed
BINS = bin
ETCS = etc
LIBS = lib
PATH = opt/UMobj
NAME = UMobj

all:

install: all
	$(INSTALL) -o root -g root -m 0755 -d $(DESTDIR)
	$(INSTALL) -o root -g root -m 0755 -d $(DESTDIR)/$(PATH)
	$(INSTALL) -o root -g root -m 0755 -d $(DESTDIR)/$(PATH)/$(BINS)
	$(INSTALL) -o root -g root -m 0755 -d $(DESTDIR)/$(PATH)/$(ETCS)
	$(INSTALL) -o root -g root -m 0755 -d $(DESTDIR)/$(PATH)/$(LIBS)
	for bin in `/bin/ls $(BINS)`; do \
		$(INSTALL) $(BINS)/$$bin $(DESTDIR)/$(PATH)/$(BINS)/$$bin; \
	done
	for etc in `/bin/ls $(ETCS)`; do \
		$(INSTALL) $(ETCS)/$$etc $(DESTDIR)/$(PATH)/$(ETCS)/$$etc; \
	done
	for lib in `/bin/ls $(LIBS)/*.py`; do \
		$(INSTALL) $$lib $(DESTDIR)/$(PATH)/$$lib; \
	done

RPM:
	/bin/tar -C .. --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)
	sed "s/=VERSION=/$(VERSION)/" build/$(NAME).spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).SPEC
