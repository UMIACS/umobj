INSTALL = /usr/bin/install
SED = /bin/sed
BINS = bin
ETCS = etc
LIBS = lib
SHARE = share
MAN = share/man
BASEPATH = opt/UMobj
NAME = UMobj
TEMPDIR := $(shell mktemp -d)

all:

install: all
	$(INSTALL) -m 0755 -d $(DESTDIR)
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$(BINS)
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$(ETCS)
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$(LIBS)
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$(SHARE)
	for mandir in `/bin/find $(MAN) -type d`; do \
	    $(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$$mandir; \
	done
	$(INSTALL) -m 0755 -d $(DESTDIR)/$(BASEPATH)/$(SHARE)/doc
	for bin in `/bin/ls $(BINS)`; do \
		$(INSTALL) $(BINS)/$$bin $(DESTDIR)/$(BASEPATH)/$(BINS)/$$bin; \
	done
	for etc in `/bin/ls $(ETCS)`; do \
		$(INSTALL) $(ETCS)/$$etc $(DESTDIR)/$(BASEPATH)/$(ETCS)/$$etc; \
	done
	for man in `/bin/find $(MAN)/ -type f`; do \
		$(INSTALL) $$man $(DESTDIR)/$(BASEPATH)/$$man; \
	done
	for lib in `/bin/ls $(LIBS)/*.py`; do \
		$(INSTALL) $$lib $(DESTDIR)/$(BASEPATH)/$$lib; \
	done

	$(INSTALL) README.md $(DESTDIR)/$(BASEPATH)/$(SHARE)/doc/README.md

RPM:
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	git clone ./ $(TEMPDIR)/$(NAME)-$(VERSION)
	git --git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git checkout $(VERSION)
	/bin/tar -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	sed "s/=VERSION=/$(VERSION)/" build/$(NAME).spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rm -rf $(TEMPDIR)

RHEL5RPM:
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	git clone ./ $(TEMPDIR)/$(NAME)-$(VERSION)
	git --git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git checkout $(VERSION)
	/bin/tar -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	sed "s/=VERSION=/$(VERSION)/" build/$(NAME)-rhel5.spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rm -rf $(TEMPDIR)
