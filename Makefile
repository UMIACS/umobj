SED = sed
NAME = umobj
PYTHON = python
TEMPDIR := $(shell mktemp -d /tmp/tmp.XXXXX)

RPM:
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	git clone ./ $(TEMPDIR)/$(NAME)-$(VERSION)
	git --git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git checkout $(VERSION)
	/bin/tar -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	sed "s/=VERSION=/$(VERSION)/" $(NAME).spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec --define "python_pkg ${PYTHON}"
	rm -rf $(TEMPDIR)

RHEL5RPM:
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	git clone ./ $(TEMPDIR)/$(NAME)-$(VERSION)
	git --git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git checkout $(VERSION)
	/bin/tar -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	sed "s/=VERSION=/$(VERSION)/" build/$(NAME)-rhel5.spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rm -rf $(TEMPDIR)
