SED = sed
TAR = tar
GIT = git
NAME = umobj
PYTHON = python

VERSION = $(shell git describe --abbrev=0 --tags)
RELEASE = $(shell grep '^Release: ' umobj.spec | awk '{print $$2}')
OS_MAJOR_VERSION = $(shell lsb_release -rs | cut -f1 -d.)
OS := rhel$(OS_MAJOR_VERSION)
ARCH = noarch

ifeq ($(OS),rhel7)
	YUMREPO_LOCATION=/fs/UMyumrepos/rhel7/stable/Packages/$(ARCH)
endif
ifeq ($(OS),rhel6)
	YUMREPO_LOCATION=/fs/UMyumrepos/rhel6/stable/Packages/$(ARCH)
endif
ifeq ($(OS),rhel5)
	PYTHON=python26
	YUMREPO_LOCATION=/fs/UMyumrepos/rhel5/stable/$(ARCH)
endif

BUILDROOT := /fs/UMbuild/$(OS)

.PHONY: rpm
rpm:
	$(eval TEMPDIR := $(shell mktemp -d /tmp/tmp.XXXXX))
	mkdir -p $(TEMPDIR)/$(NAME)-$(VERSION)
	$(GIT) clone . $(TEMPDIR)/$(NAME)-$(VERSION)
	$(GIT) \
		--git-dir=$(TEMPDIR)/$(NAME)-$(VERSION)/.git \
		--work-tree=$(TEMPDIR)/$(NAME)-$(VERSION)/.git \
		checkout tags/$(VERSION)
	$(TAR) \
		-C $(TEMPDIR) \
		--exclude .git \
		-czf $(BUILDROOT)/SOURCES/$(NAME)-$(VERSION).tar.gz \
		$(NAME)-$(VERSION)
	$(SED) "s/=VERSION=/$(VERSION)/" $(NAME).spec > $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec
	rpmbuild -bb $(BUILDROOT)/SPECS/$(NAME)-$(VERSION).spec \
		--define "python ${PYTHON}"
	rm -rf $(TEMPDIR)

.PHONY: package
package:
	@echo ================================================================
	@echo cp /fs/UMbuild/$(OS)/RPMS/$(ARCH)/$(NAME)-$(VERSION)-$(RELEASE).$(ARCH).rpm $(YUMREPO_LOCATION)
	@echo createrepo /fs/UMyumrepos/$(OS)/stable

.PHONY: build
build: rpm package
