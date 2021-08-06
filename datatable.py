def UserList(request):
	# objuser = User.objects.values_list('id','username','email','first_name','last_name','groups__name','is_active','is_staff','is_superuser','userprofile__nik','userprofile__village__name','userprofile__village__id').all()
	if request.user.is_superuser:
		objuser = User.objects.all().order_by('-id')
	else:
		objuser = User.objects.all().filter(userprofile__village=request.user.userprofile.village).order_by('-id')
	data = []
	aksi = ''
	no = int(request.POST.get('start'))
	length = int(request.POST.get('length'))
	# print(r.groups__name)
	column = {'1':'username','2':'first_name','3':'last_name','4':'email','5':'is_active'}

	if request.POST.get('search[value]') != '':
		search = Q(username__icontains=request.POST.get('search[value]')) | Q(first_name__icontains=request.POST.get('search[value]')) | Q(last_name__icontains=request.POST.get('search[value]')) | Q(email__icontains=request.POST.get('search[value]'))
		objuser = objuser.filter(search)

	if request.POST.get('order[0][column]'):
		if request.POST.get('order[0][dir]') == 'asc':
			objuser= objuser.order_by(column[request.POST.get('order[0][column]')])
		elif request.POST.get('order[0][dir]') == 'desc':
			objuser= objuser.order_by('-'+column[request.POST.get('order[0][column]')])

	if int(request.POST.get('start')) != 0:
		length += int(request.POST.get('start'))

	for r in objuser[int(request.POST.get('start')):length]:
		no +=1
		if r.is_active:
			aktif = format_html('<i class="fa fa-check-circle text-success"></i>')
		else:
			aktif = format_html('<i class="fa fa-minus-circle text-danger"></i>')

		if request.user.has_perm('auth.change_user'):
			aksi = format_html('<a href="%s" class="btn btn-success btn-sm mr-2">%s</a>' % (reverse('admin:auth_user_change',args=[r.id]),_('Change')))
		if request.user.has_perm('auth.delete_user') and request.user.id is not r.id:
			if r.is_active:
				aksi += format_html('<button type="button" data-url="%s" class="btn btn-danger btn-sm" data-toggle="modal" data-target="#confirmModal" data-title="Konfirmasi Menonaktifkan Pengguna" data-status="nonaktif">%s</button>' % (reverse('admin:userprofile_userprofile_delete',args=[r.userprofile.id]),_('Nonaktif')))
			else:
				aksi += format_html('<button type="button" data-url="%s" class="btn btn-primary btn-sm" data-toggle="modal" data-target="#confirmModal" data-title="Konfirmasi Mengaktifkan Pengguna" data-status="aktif">%s</button>' % (reverse('admin:userprofile_userprofile_delete',args=[r.userprofile.id]),_('Aktivasi')))
		
		row = []
		row.append(no)
		row.append(r.username)
		row.append(r.first_name)
		row.append(r.last_name)
		row.append(r.email)
		row.append(TerakhirLogin(r.last_login))
		row.append(aktif)
		# if aksi:
		row.append(aksi)
		data.append(row)
		
	# if request.user.has_perm('auth.view_user'):
	#   print('permitted')

	cobject = User.objects.all()
	if not request.user.is_superuser:
		cobject = cobject.filter(userprofile__village=request.user.userprofile.village)

	content = {
		'draw': int(request.POST.get('draw')),
		'recordsTotal': cobject.count(),
		'recordsFiltered': objuser.count(),
		'data': data,
	}
	return JsonResponse(content)
