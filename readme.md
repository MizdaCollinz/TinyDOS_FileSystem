TinyDOS represents a simple file system implementation, to use the system run TinyDOS.py
The valid initial commands are either

	format VOLUME_NAME - This creates a fresh drive of the name "VOLUME_NAME" with 128 empty blocks where block 0 holds the volume information and the root directory
	OR
	reconnect VOLUME_NAME - This loads in an existing volume file which has been created, nested directories are lazily loaded upon use

Other commands include

	mkfile PATH/FILE_NAME - Creates an empty file in the PATH location (Path must be an existing location E.G) "/" for Root directory) 
	mkdir PATH/DIR_NAME - Creates an empty direction in the PATH location (Similar to MKFILE)

	append FILE_PATH "TEXT_TO_APPEND" - Appends TEXT_TO_APPEND to the data in the blocks occupied by the file up to a max of 512 * 12 characters
	ls DIR_PATH - Produces a list of files and directories stored in the specified directory
	print FILE_PATH - Prints out the contents of the blocks occupied by the specified file

	delfile / deldir - Both operate similarly to mkfile or mkdir except they delete the specified file, or directory if the directory is already empty
	
	quit - Used to exit the filesystem, changes were all written to the drive as they were made