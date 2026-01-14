"""Docker sandbox runner for isolated command execution.

This module provides secure command execution in isolated Docker containers:
- SandboxConfig: Configuration for sandbox environment
- SandboxRunner: Execute commands in isolated containers
- SandboxResult: Results with file change tracking
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

from importlib.metadata import version as get_version

import yaml

CONTAINMENT_IMAGE_REPO = "bpsai/paircoder-containment"

try:
    import docker
except ImportError:
    docker = None


# Docker diff kind values
DIFF_MODIFIED = 0
DIFF_CREATED = 1
DIFF_DELETED = 2

DIFF_KIND_TO_ACTION = {
    DIFF_MODIFIED: "modified",
    DIFF_CREATED: "created",
    DIFF_DELETED: "deleted",
}


@dataclass
class MountConfig:
    """Configuration for a volume mount.

    Attributes:
        source: Host path to mount (ignored for tmpfs mounts)
        target: Container path to mount to
        readonly: Whether mount is read-only
        mount_type: Type of mount - "bind" (default) or "tmpfs"
    """

    source: str
    target: str
    readonly: bool = False
    mount_type: str = "bind"  # "bind" or "tmpfs"

    def to_docker_mount(self) -> dict:
        """Convert to Docker mount configuration dict for bind mounts."""
        return {
            "bind": self.target,
            "mode": "ro" if self.readonly else "rw"
        }

    def is_tmpfs(self) -> bool:
        """Check if this is a tmpfs mount."""
        return self.mount_type == "tmpfs"


@dataclass
class FileChange:
    """Represents a file change in the sandbox.

    Attributes:
        path: Path to the changed file (relative to workspace)
        action: Type of change (created, modified, deleted)
    """

    path: str
    action: Literal["created", "modified", "deleted"]


@dataclass
class SandboxResult:
    """Result of running a command in the sandbox.

    Attributes:
        exit_code: Command exit code
        stdout: Standard output
        stderr: Standard error
        changes: List of file changes detected
    """

    exit_code: int
    stdout: str
    stderr: str
    changes: list[FileChange] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if command succeeded (exit code 0)."""
        return self.exit_code == 0

    @property
    def has_changes(self) -> bool:
        """Check if any file changes were detected."""
        return len(self.changes) > 0


@dataclass
class SandboxConfig:
    """Configuration for the Docker sandbox.

    Attributes:
        enabled: Whether sandbox is enabled
        image: Docker image to use
        memory_limit: Memory limit (e.g., "2g")
        cpu_limit: CPU limit (number of CPUs)
        network: Network mode (none, bridge, host)
        mounts: List of volume mounts
        env_passthrough: Environment variables to pass through
    """

    enabled: bool = True
    image: str = "paircoder/sandbox:latest"
    memory_limit: str = "2g"
    cpu_limit: float = 2.0
    network: str = "none"
    mounts: list[MountConfig] = field(default_factory=list)
    env_passthrough: list[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> "SandboxConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML config file

        Returns:
            SandboxConfig instance
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        sandbox_data = data.get("sandbox", {})

        mounts = []
        for mount_data in sandbox_data.get("mounts", []):
            mounts.append(MountConfig(
                source=mount_data.get("source", ""),
                target=mount_data.get("target", ""),
                readonly=mount_data.get("readonly", False)
            ))

        return cls(
            enabled=sandbox_data.get("enabled", True),
            image=sandbox_data.get("image", cls.image),
            memory_limit=sandbox_data.get("memory_limit", cls.memory_limit),
            cpu_limit=sandbox_data.get("cpu_limit", cls.cpu_limit),
            network=sandbox_data.get("network", cls.network),
            mounts=mounts,
            env_passthrough=sandbox_data.get("env_passthrough", [])
        )

    def to_docker_kwargs(self) -> dict:
        """Convert config to Docker run kwargs.

        Returns:
            Dict of kwargs for docker.containers.run()
        """
        return {
            "mem_limit": self.memory_limit,
            "nano_cpus": int(self.cpu_limit * 1e9),
            "network_mode": self.network,
        }


class SandboxRunner:
    """Runs commands in isolated Docker containers.

    Provides secure command execution with:
    - Network isolation (disabled by default)
    - Resource limits (memory, CPU)
    - File change tracking
    - Cleanup on completion

    Attributes:
        workspace: Path to workspace directory
        config: Sandbox configuration
    """

    def __init__(
        self,
        workspace: Path,
        config: Optional[SandboxConfig] = None
    ):
        """Initialize the sandbox runner.

        Args:
            workspace: Path to workspace directory to mount
            config: Sandbox configuration (uses default if None)
        """
        self.workspace = workspace
        self.config = config or SandboxConfig()
        self._current_container = None

    @staticmethod
    def is_docker_available() -> bool:
        """Check if Docker is available.

        Returns:
            True if Docker is available and running
        """
        if docker is None:
            return False

        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    def _get_docker_client(self):
        """Get Docker client, raising error if not available."""
        if docker is None:
            raise RuntimeError("Docker Python SDK not installed. Install with: pip install docker")

        try:
            return docker.from_env()
        except Exception as e:
            raise RuntimeError(f"Docker not available: {e}")

    def ensure_containment_image(self) -> str:
        """Ensure containment image is available.

        Attempts to:
        1. Use existing local image (fastest)
        2. Pull from Docker Hub (fast for most users)
        3. Build locally from Dockerfile (fallback for offline)

        Returns:
            Image tag string to use for container creation

        Raises:
            RuntimeError: If image cannot be obtained by any method
        """
        from importlib.metadata import version as get_version
        from rich.console import Console

        console = Console()

        try:
            pkg_version = get_version("bpsai-pair")
        except Exception:
            pkg_version = "latest"

        # Image tags to try (in order of preference)
        image_tags = [
            f"{CONTAINMENT_IMAGE_REPO}:{pkg_version}",  # Versioned
            f"{CONTAINMENT_IMAGE_REPO}:latest",  # Latest
            "paircoder/containment:latest",  # Legacy local name
        ]

        # Check if any image already exists locally
        for tag in image_tags:
            try:
                self._get_docker_client().images.get(tag)
                return tag
            except Exception:
                continue

        # Try to pull from Docker Hub
        console.print(f"[cyan]Pulling containment image ({CONTAINMENT_IMAGE_REPO}:{pkg_version})...[/cyan]")
        try:
            self._get_docker_client().images.pull(CONTAINMENT_IMAGE_REPO, tag=pkg_version)
            return f"{CONTAINMENT_IMAGE_REPO}:{pkg_version}"
        except Exception as pull_error:
            console.print(f"[yellow]Pull failed: {pull_error}[/yellow]")

        # Try pulling latest as fallback
        try:
            console.print("[cyan]Trying latest tag...[/cyan]")
            self._get_docker_client().images.pull(CONTAINMENT_IMAGE_REPO, tag="latest")
            return f"{CONTAINMENT_IMAGE_REPO}:latest"
        except Exception:
            pass

        # Fall back to local build
        console.print("[yellow]Building containment image locally (this may take a few minutes)...[/yellow]")
        try:
            dockerfile_path = Path(__file__).parent / "Dockerfile.containment"
            if not dockerfile_path.exists():
                raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

            image, logs = self._get_docker_client().images.build(
                path=str(dockerfile_path.parent),
                dockerfile="Dockerfile.containment",
                tag=f"paircoder/containment:latest",
                rm=True,  # Remove intermediate containers
            )
            console.print("[green]✓ Containment image built successfully[/green]")
            return "paircoder/containment:latest"
        except Exception as build_error:
            raise RuntimeError(
                f"Failed to obtain containment image.\n"
                f"Pull failed and local build failed: {build_error}\n"
                f"Ensure Docker is running and try: docker pull {CONTAINMENT_IMAGE_REPO}:latest"
            )

    def _build_volumes(self) -> tuple[dict, dict]:
        """Build volumes and tmpfs dicts for Docker run.

        Returns:
            Tuple of (volumes, tmpfs):
            - volumes: Dict of bind mounts {source: {bind: target, mode: ro/rw}}
            - tmpfs: Dict of tmpfs mounts {target: "size=1m"}
        """
        volumes = {
            str(self.workspace): {
                "bind": "/workspace",
                "mode": "rw"
            }
        }
        tmpfs_mounts = {}

        for mount in self.config.mounts:
            if mount.is_tmpfs():
                # tmpfs mount - hide the original content with empty filesystem
                tmpfs_mounts[mount.target] = "size=1m"
            else:
                # Regular bind mount
                volumes[mount.source] = mount.to_docker_mount()

        return volumes, tmpfs_mounts

    def _build_environment(self) -> dict:
        """Build environment dict from passthrough config."""
        env = {}
        for var_name in self.config.env_passthrough:
            value = os.environ.get(var_name)
            if value is not None:
                env[var_name] = value
        return env

    def _parse_diff(self, diff_output: list) -> list[FileChange]:
        """Parse Docker diff output to FileChange list.

        Args:
            diff_output: List of diff entries from container.diff()

        Returns:
            List of FileChange objects
        """
        changes = []
        workspace_prefix = "/workspace"

        for entry in diff_output:
            path = entry.get("Path", "")
            kind = entry.get("Kind", 0)

            # Only track changes in workspace
            if path.startswith(workspace_prefix):
                relative_path = path[len(workspace_prefix):].lstrip("/")
                action = DIFF_KIND_TO_ACTION.get(kind, "modified")
                changes.append(FileChange(path=relative_path, action=action))

        return changes

    def run_command(self, command: str) -> SandboxResult:
        """Run a command in the sandbox.

        Args:
            command: Command string to execute

        Returns:
            SandboxResult with exit code, output, and file changes

        Raises:
            RuntimeError: If Docker is not available
        """
        if not self.config.enabled:
            return self._run_local(command)

        client = self._get_docker_client()

        # Build volumes and tmpfs mounts
        volumes, tmpfs_mounts = self._build_volumes()

        # Build Docker run kwargs
        run_kwargs = self.config.to_docker_kwargs()
        run_kwargs.update({
            "image": self.config.image,
            "command": "sleep infinity",  # Keep container running
            "volumes": volumes,
            "environment": self._build_environment(),
            "working_dir": "/workspace",
            "detach": True,
            "remove": False,  # We'll remove manually after getting diff
        })

        # Add tmpfs mounts if any (for blocked paths)
        if tmpfs_mounts:
            run_kwargs["tmpfs"] = tmpfs_mounts

        container = None
        try:
            # Create and start container
            container = client.containers.run(**run_kwargs)
            self._current_container = container

            # Execute command in container
            exec_result = container.exec_run(
                cmd=["sh", "-c", command],
                workdir="/workspace"
            )

            # Get file changes before removing container
            try:
                diff = container.diff() or []
            except Exception:
                diff = []

            changes = self._parse_diff(diff)

            # Decode output
            stdout = exec_result.output.decode("utf-8", errors="replace") if exec_result.output else ""

            return SandboxResult(
                exit_code=exec_result.exit_code,
                stdout=stdout,
                stderr="",  # Docker exec_run combines stdout/stderr
                changes=changes
            )

        finally:
            # Always cleanup container
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            self._current_container = None

    def _run_local(self, command: str) -> SandboxResult:
        """Run command locally when sandbox is disabled.

        Args:
            command: Command to execute

        Returns:
            SandboxResult with exit code and output
        """
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(self.workspace),
            capture_output=True,
            text=True
        )

        return SandboxResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            changes=[]  # No change tracking in local mode
        )

    def _copy_from_container(self, container, src_path: str, dest_path: str) -> None:
        """Copy file from container to host.

        Args:
            container: Docker container
            src_path: Path in container
            dest_path: Path on host
        """
        import tarfile
        import io

        # Get file as tar archive
        bits, _ = container.get_archive(src_path)

        # Extract to destination
        tar_stream = io.BytesIO()
        for chunk in bits:
            tar_stream.write(chunk)
        tar_stream.seek(0)

        with tarfile.open(fileobj=tar_stream) as tar:
            tar.extractall(path=str(Path(dest_path).parent))

    def apply_changes(self, result: SandboxResult) -> None:
        """Apply changes from sandbox to host filesystem.

        Args:
            result: SandboxResult containing changes to apply

        Note:
            When using bind mounts (default), changes are already
            applied to the host filesystem. This method is for
            copy-based workflows.
        """
        # With bind mounts, changes are already on the host
        # This method exists for future copy-based sandbox modes
        pass

    def discard_changes(self, result: SandboxResult) -> None:
        """Discard changes from sandbox.

        Args:
            result: SandboxResult containing changes to discard

        Note:
            Container is already removed in run_command().
            With bind mounts, changes cannot be discarded after execution.
            This method is for future copy-based sandbox modes.
        """
        # Container already removed in run_command()
        # With bind mounts, changes are already on the host
        pass

    def run_interactive(self, command: list[str], env: dict = None, network_allowlist: list[str] = None) -> int:
        """Run an interactive command in the sandbox container.

        This method runs a command with TTY support for interactive sessions,
        suitable for running Claude Code or other terminal-based tools.

        Args:
            command: Command to run as a list (e.g., ["claude", "--flag"])
            env: Additional environment variables to set
            network_allowlist: List of domains to allow network access to.
                             If None, uses config.network setting.
                             If provided, sets up iptables rules.

        Returns:
            Exit code from the command

        Raises:
            RuntimeError: If Docker is not available
        """
        if not self.config.enabled:
            return self._run_interactive_local(command, env)

        client = self._get_docker_client()

        # Get or build the containment image
        image_tag = self.ensure_containment_image()

        # Build environment
        container_env = self._build_environment()
        if env:
            container_env.update(env)

        # Add network allowlist to environment if specified
        if network_allowlist:
            container_env["PAIRCODER_NETWORK_ALLOWLIST"] = " ".join(network_allowlist)

        # Build volumes and tmpfs mounts
        volumes, tmpfs_mounts = self._build_volumes()

        # Mount host's Claude credentials so Claude Code can authenticate
        home_dir = Path.home()
        claude_config_dir = home_dir / ".claude"
        if claude_config_dir.exists():
            volumes[str(claude_config_dir)] = {
                "bind": "/home/sandbox/.claude",
                "mode": "rw"
            }

        # Build create kwargs for containers.create()
        # Note: create() doesn't have 'detach' or 'remove' parameters
        create_kwargs = {
            "image": image_tag,
            "volumes": volumes,
            "environment": container_env,
            "working_dir": "/workspace",
            "stdin_open": True,
            "tty": True,
        }

        # Add resource limits
        create_kwargs.update(self.config.to_docker_kwargs())

        # Determine network mode and command based on allowlist
        if network_allowlist:
            # With allowlist: use keep-alive command, configure iptables, then exec
            create_kwargs["network_mode"] = "bridge"
            create_kwargs["cap_add"] = ["NET_ADMIN"]
            create_kwargs["command"] = ["sleep", "infinity"]
        else:
            # Without allowlist: run user command directly
            create_kwargs["command"] = command

        # Add tmpfs mounts if any (for blocked paths)
        if tmpfs_mounts:
            create_kwargs["tmpfs"] = tmpfs_mounts

        container = None
        try:
            # Create container but DON'T start it yet
            # dockerpty.start() will handle both starting and attaching
            container = client.containers.create(**create_kwargs)
            self._current_container = container

            if network_allowlist:
                # Start container with keep-alive command
                container.start()
                # Configure iptables rules while container is running
                self._setup_network_allowlist(container, network_allowlist)
                # Now exec the actual user command interactively
                import dockerpty
                dockerpty.exec_command(client.api, container.id, command)
            else:
                # Normal case: let dockerpty start AND attach in one operation
                # This is the correct pattern for interactive TTY sessions
                import dockerpty
                dockerpty.start(client.api, container.id)

            # Get exit code after container finishes
            container.reload()
            exit_code = container.attrs.get("State", {}).get("ExitCode", 1)
            return exit_code

        except ImportError:
            # dockerpty not available, fall back to exec_run
            if container:
                exec_result = container.exec_run(
                    cmd=command,
                    workdir="/workspace",
                    tty=True,
                    stdin=True,
                )
                return exec_result.exit_code
            return 1

        finally:
            if container:
                try:
                    container.stop(timeout=5)
                    container.remove(force=True)
                except Exception:
                    pass
            self._current_container = None

    def _run_interactive_local(
        self,
        command: list[str],
        env: Optional[dict[str, str]] = None,
    ) -> int:
        """Run interactive command locally when sandbox is disabled.

        Args:
            command: Command to run as a list
            env: Additional environment variables

        Returns:
            Exit code from the command
        """
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        result = subprocess.run(
            command,
            cwd=str(self.workspace),
            env=run_env,
        )
        return result.returncode

    def _setup_network_allowlist(
        self,
        container,
        allowed_domains: list[str],
    ) -> None:
        """Set up iptables rules to restrict network to allowed domains.

        Args:
            container: Docker container to configure
            allowed_domains: List of domains to allow
        """
        # Build iptables commands
        iptables_cmds = []

        # Allow localhost
        iptables_cmds.append("iptables -A OUTPUT -d 127.0.0.0/8 -j ACCEPT")
        iptables_cmds.append("iptables -A OUTPUT -o lo -j ACCEPT")

        # Allow DNS (needed to resolve domains)
        iptables_cmds.append("iptables -A OUTPUT -p udp --dport 53 -j ACCEPT")
        iptables_cmds.append("iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT")

        # Allow established connections
        iptables_cmds.append("iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")

        # Resolve and allow each domain
        for domain in allowed_domains:
            # Use dig to resolve domain to IPs
            resolve_cmd = f"dig +short {domain} | grep -E '^[0-9]+\\.' | while read ip; do iptables -A OUTPUT -d $ip -j ACCEPT; done"
            iptables_cmds.append(resolve_cmd)

        # Block all other outbound traffic
        iptables_cmds.append("iptables -A OUTPUT -j REJECT")

        # Execute all commands
        script = " && ".join(iptables_cmds)
        container.exec_run(
            cmd=["sh", "-c", script],
            user="root",
        )


def containment_config_to_mounts(
    config: "ContainmentConfig",
    project_root: Path,
) -> tuple[list[MountConfig], list[str]]:
    """Convert ContainmentConfig to Docker mount configuration.

    Maps the three-tier access control to Docker volumes:
    - Blocked paths: Overlaid with empty tmpfs (content hidden/inaccessible)
    - Readonly paths: Mounted with readonly=True (OS-enforced)
    - Everything else: Part of workspace mount (read-write)

    The mount order matters! Docker processes mounts in order, so:
    1. Base workspace mount (everything visible)
    2. Blocked paths overlaid with tmpfs (hides original content)
    3. Readonly paths overlaid with ro bind mount (protects from writes)

    Args:
        config: ContainmentConfig with path restrictions
        project_root: Root directory of the project

    Returns:
        Tuple of (mounts, blocked_paths):
        - mounts: List of MountConfig for Docker volumes (includes tmpfs for blocked)
        - blocked_paths: List of paths that are blocked (for reference/logging)
    """
    from bpsai_pair.core.config import ContainmentConfig  # Import for type checking

    mounts = []
    blocked = []

    # Base workspace mount (read-write for everything not specifically restricted)
    # Note: We mount the full workspace, then overlay with other mounts
    mounts.append(MountConfig(
        source=str(project_root.resolve()),
        target="/workspace",
        readonly=False
    ))

    # Blocked directories (Tier 1 - overlaid with empty tmpfs)
    # tmpfs mount hides the original directory content
    # Only mount paths that actually exist to avoid creating phantom files
    for dir_path in config.blocked_directories:
        dir_path = dir_path.rstrip("/")
        full_path = project_root / dir_path
        if full_path.exists():
            blocked.append(dir_path)
            mounts.append(MountConfig(
                source="",  # Not used for tmpfs
                target=f"/workspace/{dir_path}",
                readonly=False,  # tmpfs is writable but empty
                mount_type="tmpfs"
            ))

    # Blocked files (Tier 1 - overlaid with empty tmpfs)
    # Note: For files, we create an empty directory mount which effectively
    # makes the file inaccessible (it becomes a directory)
    # Only mount paths that actually exist to avoid creating phantom files
    for file_path in config.blocked_files:
        full_path = project_root / file_path
        if full_path.exists():
            blocked.append(file_path)
            mounts.append(MountConfig(
                source="",  # Not used for tmpfs
                target=f"/workspace/{file_path}",
                readonly=False,
                mount_type="tmpfs"
            ))

    # Readonly directories (Tier 2 - mounted read-only)
    # These overlay the base workspace mount
    for dir_path in config.readonly_directories:
        dir_path = dir_path.rstrip("/")
        full_path = project_root / dir_path
        if full_path.exists():
            mounts.append(MountConfig(
                source=str(full_path.resolve()),
                target=f"/workspace/{dir_path}",
                readonly=True  # OS-enforced read-only!
            ))

    # Readonly files (Tier 2 - mounted read-only)
    for file_path in config.readonly_files:
        full_path = project_root / file_path
        if full_path.exists():
            mounts.append(MountConfig(
                source=str(full_path.resolve()),
                target=f"/workspace/{file_path}",
                readonly=True  # OS-enforced read-only!
            ))

    return mounts, blocked
