- [ ] Split swift_libs from a shared library into a standard Python package
    - [ ] Separate Red-dependent code from generic utilities
        - [ ] Determine what to do with Red specific code - could make generic versions w/ Red specific counterparts or move Red specific features into an ext package
    - [ ] Move swift_libs into separate GitLab repository
    - [ ] Setup a meta shared library to install the new package

The primary benefits from switching to using a package instead of a shared library is
the following:

- We're no longer directly tied to shared libraries (with the exception of installing, but can be worked around
  by simply adding the package as a dependency to all cogs)
- Simpler portability between non-Red bots
- Much clearer code separation between cogs and swift_libs
- We'll no longer be unsure if we'll be placed under either `cog_shared.swift_libs` or `swift_libs`
- More flexibility for versioning, allowing for tarballs with tagged commits as the package install source;
  though admittedly this would only help since I'm horrible at making changes then letting them build up
  in my working directory, while also making other changes based on changes here in cogs
