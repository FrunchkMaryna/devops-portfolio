package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

var categories = map[string][]string{
	"Documents": {".pdf", ".docx", ".txt", ".csv", ".xlsx"},
	"Images":    {".jpg", ".jpeg", ".png", ".gif"},
	"Music":     {".mp3", ".wav", ".flac"},
	"Videos":    {".mp4", ".avi", ".mkv"},
	"Archives":  {".zip", ".rar", ".tar", ".gz"},
}

func main() {
	path := flag.String("path", ".", "Path to the folder to organize")
	dryRun := flag.Bool("dry-run", false, "Show actions without moving files")
	copyMode := flag.Bool("copy", false, "Copy files instead of moving")
	flag.Parse()

	files, err := os.ReadDir(*path)
	if err != nil {
		fmt.Println("Error reading directory:", err)
		return
	}

	summary := make(map[string]int)

	for _, file := range files {
		if file.IsDir() {
			continue
		}

		ext := strings.ToLower(filepath.Ext(file.Name()))
		category := getCategory(ext)
		targetDir := filepath.Join(*path, category)

		sourcePath := filepath.Join(*path, file.Name())
		targetPath := filepath.Join(targetDir, file.Name())

		if *dryRun {
			fmt.Printf("[DRY-RUN] %s → %s\n", sourcePath, targetPath)
			summary[category]++
			continue
		}

		os.MkdirAll(targetDir, os.ModePerm)

		if *copyMode {
			copyFile(sourcePath, targetPath)
		} else {
			os.Rename(sourcePath, targetPath)
		}

		fmt.Printf("Moved: %s → %s\n", file.Name(), category)
		summary[category]++
	}

	fmt.Println("\n=== Summary ===")
	for cat, count := range summary {
		fmt.Printf("%-10s: %d files\n", cat, count)
	}
	fmt.Println("Done!")
}

func getCategory(ext string) string {
	for cat, exts := range categories {
		for _, e := range exts {
			if e == ext {
				return cat
			}
		}
	}
	return "Others"
}

func copyFile(src, dst string) error {
	source, err := os.Open(src)
	if err != nil {
		return err
	}
	defer source.Close()

	destination, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer destination.Close()

	_, err = io.Copy(destination, source)
	return err
}
