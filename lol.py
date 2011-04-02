VIDEOTHEQUE = "videotheque\\"
images = []
images.append("")

for i in range(1,81):
	print "image %s" % i
	f = open(VIDEOTHEQUE + "mavideo\\" + str(i) + ".jpg", "rb")
	images.append(f.read())
	f.close()


for i in range(1,81):
	print "image %s" % i
	#j = 0
	#for ch in images[i]:
	#	j = j + 1

	print "longueur = %s " % len(images[i])
	raw_input()