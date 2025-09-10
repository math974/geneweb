# GWU

## Summary

Export a database to a GeneWeb file (.gw)

## Arguments

### Native
```
-odir ODIR            Create files from original name in
                      directory (else on -o file)
-isolated             Export isolated persons (work only
                      if export all database)
-old_gw               Do not export additional fields (for
                      backward compatibility: < 7.00)
-raw                  Raw output (without possible utf-8
                      conversion)
-sep SEP              To use together with the option
                      "-odir": separate this person and
                      all ancestors
-sep_only_file SEP_ONLY_FILE
                      With option "-sep", tells to
                      separate only groups of that file
-sep_limit SEP_LIMIT  When using option "-sep", sets the
                      limit for reconnecting isolated
                      family groups
-all_files            Save all content of notes_d in the
                      .gw file, including files without
                      Wiki links
```

### Added from `gwexport`

```
-a N                  maximum generation of the root's
                      ascendants
-ad N                 maximum generation of the root's
                      ascendants descendants
-key KEY              key reference of root person. Used
                      for -a/-d options. Can be used
                      multiple times. Key format is "First
                      Name.occ SURNAME"
-c NUM                when a person is born less than
                      <num> years ago, it is not exported
                      unless it is Public. All the spouses
                      and descendants are also censored.
-charset {ASCII,ANSEL,ANSI,UTF-8}
                      set charset; default is UTF-8
-d N                  maximum generation of the root's
                      descendants
-mem                  save memory space, but slower
-nn                   no (database) notes
-nnn                  no notes (implies -nn)
-nopicture            don't extract individual picture
-o FILE               output file name (default: stdout)
-parentship           select individuals involved in
                      parentship computation between pairs
                      of keys. Pairs must be defined with
                      -key option, descendant first: e.g.
                      -key "Descendant.0 SURNAME" -key
                      "Ancestor.0 SURNAME". If multiple
                      pairs are provided, union of persons
                      are returned.
-picture-path         extract pictures path
-s SN                 select this surname (option usable
                      several times, union of surnames
                      will be used)
-source SRC           replace individuals and families
                      sources. Also delete event sources
-v                    verbose
```
