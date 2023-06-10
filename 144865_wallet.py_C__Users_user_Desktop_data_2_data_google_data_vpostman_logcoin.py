import sys, proto
success,newkey= proto.wallet(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
print newkey if success else ""
exit(success-1)
