SED = sed
TAR = tar
GIT = git
PACKAGE = umobj
PYTHON = python

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
	$(SED) "s/=VERSION=/$(VERSION)/" $(PACKAGE).spec > $(BUILDROOT)/SPECS/$(PACKAGE)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(PACKAGE)-$(VERSION).spec --define "python ${PYTHON}"
	rm -rf $(TEMPDIR)

.PHONY: build
build: rpm

.PHONY: tag
tag:
	$(SED) -i 's/__version__ = .*/__version__ = "$(VERSION)"/g' $(PACKAGE)/__init__.py
	$(GIT) add $(PACKAGE)/__init__.py
	$(GIT) commit -m "Tagging $(VERSION)"
	$(GIT) tag -a $(VERSION) -m "Tagging $(VERSION)"

.PHONY: sdist
sdist:
	/usr/bin/virtualenv /tmp/buildenv
	/tmp/buildenv/bin/pip install --upgrade setuptools
	/tmp/buildenv/bin/python setup.py sdist

.PHONY: clean
clean:
	rm -rf dist/
