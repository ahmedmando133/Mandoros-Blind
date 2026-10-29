"""Small Windows launcher for the automated Mandros Blind pipeline.

Double-click ``RUN_MANDROS_BLIND.vbs`` to open this window without a console.
The pipeline starts automatically and keeps all scientific work in ``run.py``.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "outputs"


class MandrosBlindWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Mandros Blind")
        self.root.geometry("900x590")
        self.root.minsize(720, 480)
        self.root.configure(bg="#F4F8F7")
        self.process: subprocess.Popen[str] | None = None
        self.messages: queue.Queue[tuple[str, str | int]] = queue.Queue()
        self.latest_run: Path | None = None

        self._build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(150, self._drain_messages)
        self.root.after(500, self.start_pipeline)

    def _build_interface(self) -> None:
        header = tk.Frame(self.root, bg="#17324D", padx=24, pady=20)
        header.pack(fill="x")
        tk.Label(
            header,
            text="MANDROS BLIND",
            bg="#17324D",
            fg="white",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="e")
        tk.Label(
            header,
            text="التشغيل الآلي لفحص وتصحيح ملفات الدراسات",
            bg="#17324D",
            fg="#D9EFEB",
            font=("Segoe UI", 11),
        ).pack(anchor="e", pady=(4, 0))

        body = tk.Frame(self.root, bg="#F4F8F7", padx=24, pady=18)
        body.pack(fill="both", expand=True)

        self.status = tk.StringVar(value="جاري الاستعداد للتشغيل...")
        tk.Label(
            body,
            textvariable=self.status,
            bg="#F4F8F7",
            fg="#17324D",
            font=("Segoe UI", 12, "bold"),
            anchor="e",
        ).pack(fill="x")

        self.progress = ttk.Progressbar(body, mode="indeterminate")
        self.progress.pack(fill="x", pady=(10, 14))

        self.log = ScrolledText(
            body,
            height=18,
            wrap="word",
            font=("Consolas", 9),
            bg="white",
            fg="#17324D",
            relief="solid",
            borderwidth=1,
        )
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

        buttons = tk.Frame(body, bg="#F4F8F7", pady=14)
        buttons.pack(fill="x")
        self.run_button = tk.Button(
            buttons,
            text="تشغيل مرة أخرى",
            command=self.start_pipeline,
            state="disabled",
            bg="#0F766E",
            fg="white",
            activebackground="#0B5F59",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8,
            relief="flat",
        )
        self.run_button.pack(side="right")

        self.open_button = tk.Button(
            buttons,
            text="فتح مجلد النتائج",
            command=self.open_results,
            state="disabled",
            bg="#17324D",
            fg="white",
            activebackground="#244765",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8,
            relief="flat",
        )
        self.open_button.pack(side="right", padx=(0, 10))

    @staticmethod
    def _console_python() -> Path:
        current = Path(sys.executable)
        if current.name.lower() == "pythonw.exe":
            console = current.with_name("python.exe")
            if console.is_file():
                return console
        return current

    def _append_log(self, line: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", line.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_pipeline(self) -> None:
        if self.process and self.process.poll() is None:
            return
        self.run_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.status.set("جاري تشغيل Mandros Blind ومعالجة الملفات الموجودة داخل data...")
        self.progress.start(12)
        self._append_log("Starting Mandros Blind automated pipeline...")

        command = [str(self._console_python()), "-u", str(ROOT / "run.py")]
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        try:
            self.process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creation_flags,
            )
        except Exception as exc:
            self.progress.stop()
            self.status.set("تعذر بدء التشغيل")
            self.run_button.configure(state="normal")
            messagebox.showerror("Mandros Blind", f"تعذر تشغيل النظام:\n{exc}")
            return
        threading.Thread(target=self._read_process, daemon=True).start()

    def _read_process(self) -> None:
        assert self.process is not None
        assert self.process.stdout is not None
        for line in self.process.stdout:
            self.messages.put(("log", line))
        code = self.process.wait()
        self.messages.put(("done", code))

    def _drain_messages(self) -> None:
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == "log":
                    self._append_log(str(value))
                elif kind == "done":
                    self._finished(int(value))
        except queue.Empty:
            pass
        self.root.after(150, self._drain_messages)

    def _finished(self, return_code: int) -> None:
        self.progress.stop()
        stable_results = OUTPUT_ROOT / "studies"
        self.latest_run = stable_results if stable_results.is_dir() else OUTPUT_ROOT
        self.run_button.configure(state="normal")
        if self.latest_run:
            self.open_button.configure(state="normal")
        if return_code == 0:
            self.status.set("اكتمل التشغيل بنجاح. يمكنك فتح مجلد النتائج.")
            self._append_log("Pipeline completed successfully.")
        else:
            self.status.set("اكتمل التشغيل مع أخطاء أو ملفات تحتاج مراجعة. راجعي سجل التشغيل.")
            self._append_log(f"Pipeline finished with exit code {return_code}.")

    def open_results(self) -> None:
        target = self.latest_run or (OUTPUT_ROOT / "studies")
        target.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(target)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(target)])

    def _close(self) -> None:
        if self.process and self.process.poll() is None:
            if not messagebox.askyesno("Mandros Blind", "التشغيل ما زال مستمرًا. هل تريدين إغلاق النافذة وإيقافه؟"):
                return
            self.process.terminate()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    MandrosBlindWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
