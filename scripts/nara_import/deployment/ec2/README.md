# EC2 Deployment Scripts

Automated EC2 deployment for NARA collection importer with auto-shutdown.

## Quick Start

```bash
# Test import (verify auto-shutdown works)
./deploy.sh test

# Full import (4-8 hours)
./deploy.sh full
```

## Scripts

- **deploy.sh** - Main deployment script (creates instance, runs import, auto-shutdown)
- **monitor.sh** - Monitor running instances and view logs
- **cleanup.sh** - Terminate instances and clean up resources
- **user-data-test.sh** - User data for test import
- **user-data-full.sh** - User data for full import

## Auto-Shutdown

Both test and full imports **automatically shutdown** the EC2 instance when complete:

- **Test mode**: ~3 minutes total (60 sec after 2-min import)
- **Full mode**: ~4-8 hours total (60 sec after import completes)
- **On failure**: Instance stays running for debugging

## See Also

- [../README.md](../README.md) - Complete deployment documentation
- [../../README.md](../../README.md) - Main project README

