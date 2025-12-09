package main

import (
    "flag"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "strings"
)

var (
    srcDir  = flag.String("src", ".", "source directory")
    mode    = flag.String("mode", "move", "mode: move|copy|dryrun")
    byExt   = flag.Bool("by-ext", true, "organize by extension")
    
    // ОНОВЛЕНА МАПА: Додані розширення для кращого сортування
    extMap  = map[string]string{
        ".jpg": "images", ".jpeg": "images", ".png": "images", ".gif": "images",
        ".mp4": "videos", ".mkv": "videos", ".mp3": "audio",
        ".zip": "archives", ".tar": "archives", ".gz": "archives",
        
        // Документи та звіти
        ".pdf": "documents", ".docx": "documents", ".txt": "documents", 
        ".html": "reports", ".csv": "reports", ".json": "reports", // Нові
        
        // Код та скрипти
        ".go": "code", ".py": "code", ".js": "code",
        ".sh": "scripts", // Нове
        ".yml": "config", ".md": "documents", // Нові
    }
)

// ... (Функції ensureDir, copyFile, moveFile, targetDirFor залишаються без змін) ...

func targetDirFor(name string) string {
    ext := strings.ToLower(filepath.Ext(name))
    if dir, ok := extMap[ext]; ok {
        return dir
    }
    return "others"
}

func main() {
    flag.Parse()
    fmt.Printf("Running in %s mode, src=%s\n", *mode, *srcDir)

    err := filepath.Walk(*srcDir, func(path string, info os.FileInfo, err error) error {
        if err != nil { return err }

        // --- ЛОГІКА ВИКЛЮЧЕННЯ (IGNORING LOGIC) ---
        
        // 1. Ігнорувати директорії
        if info.IsDir() {
            // Ігнорувати папки .git та .github (критичні для репозиторію)
            if info.Name() == ".git" || info.Name() == ".github" {
                return filepath.SkipDir
            }
            // Ігнорувати папки, створені організатором (щоб уникнути нескінченного циклу)
            for _, dir := range extMap {
                if info.Name() == dir {
                    return filepath.SkipDir
                }
            }
            return nil
        }

        // 2. Ігнорувати приховані файли (якщо це не .git або .github)
        if strings.HasPrefix(info.Name(), ".") { 
            // Якщо файл знаходиться у корені srcDir і починається з крапки, ігнорувати його (наприклад, .gitignore)
            if filepath.Dir(path) == *srcDir {
                 return nil
            }
        }
        
        // 3. Ігнорувати сам виконуваний файл CLI
        if info.Name() == filepath.Base(os.Args[0]) {
            return nil
        }
        
        // Існуюча логіка для ігнорування вже відсортованих папок (можливо, потребує розширення)
        // Наразі ігноруються лише "images" та "videos"
        if strings.Contains(path, string(os.PathSeparator)+"images"+string(os.PathSeparator)) ||
            strings.Contains(path, string(os.PathSeparator)+"videos"+string(os.PathSeparator)) {
             return nil
        }
        
        // ------------------------------------------

        rel := path
        
        // ... (решта логіки залишається без змін) ...
        var target string
        if *byExt {
            target = filepath.Join(*srcDir, targetDirFor(info.Name()))
        } else {
            target = filepath.Join(*srcDir, "unsorted")
        }
        if err := ensureDir(target); err != nil {
            return err
        }
        dst := filepath.Join(target, info.Name())

        switch *mode {
        case "dryrun":
            // Використання rel та dst для виводу
            fmt.Printf("[DRYRUN] %s -> %s\n", rel, dst) 
        // ... (решта case-блоків move, copy, default) ...
        case "copy":
            fmt.Printf("[COPY ] %s -> %s\n", rel, dst)
            if err := copyFile(path, dst); err != nil {
                fmt.Fprintf(os.Stderr, "copy error: %v\n", err)
            }
        case "move":
            fmt.Printf("[MOVE ] %s -> %s\n", rel, dst)
            if err := moveFile(path, dst); err != nil {
                // fallback to copy+remove
                if err := copyFile(path, dst); err != nil {
                    fmt.Fprintf(os.Stderr, "move error: %v\n", err)
                } else {
                    os.Remove(path)
                }
            }
        default:
            fmt.Fprintf(os.Stderr, "Unknown mode: %s\n", *mode)
        }
        return nil
    })
    if err != nil {
        fmt.Fprintf(os.Stderr, "walk error: %v\n", err)
        os.Exit(1)
    }
    fmt.Println("Done.")
}