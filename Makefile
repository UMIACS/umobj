SED = sed
TAR = tar
GIT = git

PACKAGE = umobj

VERSION = $(shell git describe --abbrev=0 --tags)
RELEASE = $(shell grep '^Release: ' umobj.spec | awk '{print $$2}')
OS_MAJOR_VERSION = $(shell lsb_release -rs | cut -f1 -d.)
OS := rhel$(OS_MAJOR_VERSION)
ARCH = noarch

BUILDROOT := /srv/build/$(OS)

.PHONY: rpm
rpm:
	$(eval TEMPDIR := $(shell mktemp -d /tmp/tmp.XXXXX))
	mkdir -p $(TEMPDIR)/$(PACKAGE)-$(VERSION)
	$(GIT) clone . $(TEMPDIR)/$(PACKAGE)-$(VERSION)
	$(GIT) \
		--git-dir=$(TEMPDIR)/$(PACKAGE)-$(VERSION)/.git \
		--work-tree=$(TEMPDIR)/$(PACKAGE)-$(VERSION) \
		checkout tags/$(VERSION)
	$(TAR) -C $(TEMPDIR) --exclude .git -czf $(BUILDROOT)/SOURCES/$(PACKAGE)-$(VERSION).tar.gz $(PACKAGE)-$(VERSION)
	rpmbuild -bb $(PACKAGE).spec --define "python ${PYTHON}" --define "version ${VERSION}"
	rm -rf $(TEMPDIR)

.PHONY: build
build: rpm

.PHONY: tag
tag:
	$(SED) -i 's/__version__ = .*/__version__ = "$(VERSION)"/g' $(PACKAGE)/__init__.py
	$(GIT) add $(PACKAGE)/__init__.py
	$(GIT) commit -m "Tagging $(VERSION)"
	$(GIT) tag -a $(VERSION) -m "Tagging $(VERSION)"

.PHONY: clean
clean:
	rm -rf dist/
