SED = sed
TAR = tar
GIT = git
NAME = umobj
PYTHON = python
TEMPDIR := $(shell mktemp -d /tmp/tmp.XXXXX)

RPM:
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	$(GIT) clone ./ $(TEMPDIR)/$(NAME)-$(VERSION)
	$(GIT) --git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git checkout $(VERSION)
	$(TAR) -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	$(SED) "s/=VERSION=/$(VERSION)/" $(NAME).spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec --define "python ${PYTHON}"
	rm -rf $(TEMPDIR)
