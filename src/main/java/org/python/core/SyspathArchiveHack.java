package org.python.core;

import java.io.IOException;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class SyspathArchiveHack extends SyspathArchive {
	

    private ZipFile zipfileToo;

    public SyspathArchiveHack(ZipFile zipFile, String archiveName) throws IOException {
        super(zipFile, archiveName);
        zipfileToo = zipFile;
    }

    ZipEntry getEntry(String entryName) {
        return zipfileToo.getEntry(entryName);
    }

}
