package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"regexp"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

type App struct {
	ctx context.Context
}

func NewApp() *App { return &App{} }

func (a *App) startup(ctx context.Context) { a.ctx = ctx }

func (a *App) SelectFolder() string {
	folder, _ := runtime.OpenDirectoryDialog(a.ctx, runtime.OpenDialogOptions{
		Title: "Select Onyx Project Folder",
	})
	return folder
}

func (a *App) GetHTMLFiles(dir string) []string {
	var files []string
	entries, _ := os.ReadDir(dir)
	for _, entry := range entries {
		if !entry.IsDir() && filepath.Ext(entry.Name()) == ".html" {
			files = append(files, entry.Name())
		}
	}
	return files
}

// Fixed: Returning (string, error) correctly for Wails Bridge
func (a *App) ReadFileContent(dir string, name string) (string, error) {
	path := filepath.Join(dir, name)
	content, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(content), nil
}

func (a *App) SaveCode(dir string, name string, code string) string {
	path := filepath.Join(dir, name)
	err := os.WriteFile(path, []byte(code), 0644)
	if err != nil {
		return "Error saving file"
	}
	return "File Saved Successfully"
}

// Native Create: Uses OS Save Dialog instead of JS prompt
func (a *App) CreateFile(dir string) string {
	name, _ := runtime.SaveFileDialog(a.ctx, runtime.SaveDialogOptions{
		Title:            "Create New Page",
		DefaultDirectory: dir,
		Filters:          []runtime.FileFilter{{DisplayName: "HTML Files", Pattern: "*.html"}},
	})
	if name == "" {
		return ""
	}
	tpl := "<!DOCTYPE html>\n<html>\n<head><title>New Page</title></head>\n<body>\n<h1>New Page</h1>\n</body>\n</html>"
	os.WriteFile(name, []byte(tpl), 0644)
	return "Created: " + filepath.Base(name)
}

// Native Delete: Uses OS Confirmation Dialog
func (a *App) DeleteFile(dir string, name string) string {
	res, _ := runtime.MessageDialog(a.ctx, runtime.MessageDialogOptions{
		Type:    runtime.QuestionDialog,
		Title:   "Confirm Delete",
		Message: fmt.Sprintf("Are you sure you want to delete %s?", name),
	})
	if res == "No" || res == "Cancel" {
		return "Cancelled"
	}
	os.Remove(filepath.Join(dir, name))
	return "File Deleted"
}

func (a *App) SyncFile(dir string, name string, newTitle string) string {
	path := filepath.Join(dir, name)
	content, _ := os.ReadFile(path)
	reT := regexp.MustCompile(`(?i)<title>.*?</title>`)
	reH := regexp.MustCompile(`(?i)<h1>.*?</h1>`)
	updated := reT.ReplaceAllString(string(content), "<title>"+newTitle+"</title>")
	updated = reH.ReplaceAllString(updated, "<h1>"+newTitle+"</h1>")
	os.WriteFile(path, []byte(updated), 0644)
	return "Sync Successful"
}
