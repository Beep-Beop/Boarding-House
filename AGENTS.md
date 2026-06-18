# Project Preferences

## Dashboard Loading Style

Always use `CTkProgressBar(mode="indeterminate")` for loading states in dashboard views. Pattern:

```python
self._dash_progress = ctk.CTkProgressBar(parent, mode="indeterminate",
                                          fg_color=self.entry_border,
                                          progress_color=self.primary_color)
self._dash_progress.pack(fill="x", pady=(0, 10))
self._dash_progress.start()
# ... fetch data in thread ...
# When done:
self._dash_progress.stop()
self._dash_progress.pack_forget()
```

- One progress bar per dashboard view (not one per section)
- Start before all fetches, stop when all return
- Use `ThreadPoolExecutor` for parallel data loading where appropriate
