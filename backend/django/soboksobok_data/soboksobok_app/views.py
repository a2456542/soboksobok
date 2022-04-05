from django.shortcuts import render
from .models import Welfare
from .models import User
from .models import Selectfamily
from .models import Selecttarget
import pandas as pd
import json
import os 
from pandas import Series,DataFrame
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.
def index(request):
	return render(request,'index.html')

# db 연결 확인코드
# def qna_view(request):
# 	qnas=Qna.objects.all()
# 	return render(request,'qna.html',{'qnas':qnas})

def insertWelfare(request):
	print("현재 os 경로",os.getcwd())
	file_path = os.getcwd()+"/data/welfare_json.json"
	with open(file_path, "r", encoding='UTF8') as json_file:
		json_data = json.load(json_file)
		welfares=[]
		for i in json_data:
			# print("복지 하나",i,"\n")
			welfare=Welfare()
			welfare.welfare_id=i['welfare_id']
			welfare.welfare_ori_id=i['welfare_ori_id']
			welfare.welfare_service_name=i['welfare_service_name']
			welfare.welfare_dept_name =i['welfare_dept_name']
			welfare.welfare_target_detail=i['welfare_target_detail']
			welfare.welfare_crit=i['welfare_crit']
			welfare.welfare_service_content=i['welfare_service_content']
			welfare.welfare_howto=i['welfare_howto']
			welfare.welfare_phone=i['welfare_phone']
			welfare.welfare_site_name=i['welfare_site_name']
			welfare.welfare_site_link=i['welfare_site_link']
			welfare.welfare_area=i['welfare_area']
			welfare.welfare_gu=i['welfare_gu']
			welfare.welfare_child=i['welfare_child']
			welfare.welfare_contact=i['welfare_contact']
			# welfare_name
			# welfare_group

			welfares.append(welfare)
		Welfare.objects.bulk_create(welfares)

	return render(request,'insert_welfare.html')

@api_view(['GET'])
def insertusergroupAPI_DBSCAN(request,user_seq):
	# user_seq=1; #유저 아이디 받아오기
	user=User.objects.filter(user_seq=user_seq);
	# print("user확인 :: ",user.values())
	#QuerySet()은 리스트이고, 객체는 dictionary 이므로 <variable name>[index]['key'] 의 형식으로 value값에 접근이 가능하다
	# print("user이름 :: ",user.values()[0]['username'])
	selectfamily=Selectfamily.objects.filter(user_seq=user_seq);
	selecttarget=Selecttarget.objects.filter(user_seq=user_seq);
	# print("selectfamily :: ",selectfamily.values())
	# print("selecttarget :: ",selecttarget.values())

	result=arrange(user,selectfamily,selecttarget)
	result_word=word_arrange(user,selectfamily,selecttarget)
	user_vector=user_vectorization(result)
	# print(user_vector)
	# DBSCAN or Spherical K-Means
	user_group_mapping_dbscan(user_vector,user_seq,result_word)

	return Response("success")

def arrange(user,selectfamily,selecttarget):
	total = []
	arr=[user.values()[0],selectfamily.values(),selecttarget.values()]
	print("user:: ",user.values())
	cur=arr[0]
	# area=1
	# gwangju=0
	# area_gu=1
	# gwangju_gu=0
	# gwangju_gwangsan=0
	# gwangju_nam=0
	# gwangju_dong=0
	# gwangju_buk=0
	# gwangju_seo=0
	age09=0
	age1019=0
	age2029=0
	age3039=0
	age60=0
	student=0
	inoccupation=0
	startup=0
	farmerfisherman=0
	smallcompony=0
	job_defalut=0
	child_ok=0
	child_empty=0
	female=0
	male=0
	not_have_house=0
	pregnant=0
	alone=0
	other_culture=0
	many_child=0
	national_merit=0
	disabled=0
	new=0
	single_parent=0
	many_family=0
	alone_old_man=0
	vulnerable=0
	none_of_them=0  # 초기 값 설정
	
	# row=cur.iloc[j] #유저 한명
	id=int(cur['user_seq']) #유저 아이디
	row=cur['age']
	if row=='1':
		age09=1
	elif row=='2':
		age1019=1
	elif row=='3':
		age2029=1
	elif row=='4':
		age3039=1
	elif row=='5':
		age60=1
	elif row=='6':
		age09=1
		age1019=1
		age2029=1
		age3039=1
		age60=1
	# 연령대 끝
	row=cur['child']
	if row=='1':
		child_ok=1
	elif row=='2':
		child_empty=1
	# 자녀유무 끝
	row=cur['female']
	if row==1:
		female=1
	row=cur['male']
	if row==1:
		male=1
	# user 데이터 끝 
	for l in range(1,len(arr)):
		welfare_data=arr[l] # selectfamily, selecttarget 데이터
		total_idx=len(welfare_data)
		# print("total_idx",total_idx)
		if(l==1): #selectfamily
			for j in range(total_idx):
				row=welfare_data[j]
				row=row['family_id']
				if(row==0):
					not_have_house=1
				elif(row==1):
					pregnant=1
				elif(row==2):
					alone=1
				elif(row==3):
					other_culture=1
				elif(row==4):
					many_child=1
				elif(row==5):
					national_merit=1
				elif(row==6):
					disabled=1
				elif(row==7):
					new=1
				elif(row==8):
					single_parent=1
				elif(row==9):
					many_family=1
				elif(row==10):
					alone_old_man=1
				elif(row==11):
					vulnerable=1
				elif(row==12):
					none_of_them=1
			# 가구 끝 
		if(l==2): #selecttarget
			for j in range(total_idx):
				row=welfare_data[j]
				row=row['target_id']
				if(row==0):
					student=1
				elif(row==1):
					inoccupation=1
				elif(row==2):
					startup=1
				elif(row==3):
					farmerfisherman=1
				elif(row==4):
					smallcompony=1
				elif(row==5):
					job_defalut=1
			# 대상 끝
	# 데이터 받기 완료        
	d=pd.DataFrame({
		'아동':[age09],
		'청소년':[age1019],
		'청년':[age2029],
		'중장년':[age3039],
		'노년':[age60],
		'학생':[student],
		'무직':[inoccupation],
		'창업':[startup],
		'농어업인':[farmerfisherman],
		'중소기업':[smallcompony],
		'일반':[job_defalut],
		'자녀여부 있음':[child_ok],
		'자녀여부 없음':[child_empty],
		'여성':[female],
		'남성':[male],
		'무주택자':[not_have_house],
		'임산부':[pregnant],
		'1인가구':[alone],
		'다문화/탈북민':[other_culture],
		'다자녀':[many_child],
		'보훈대상자/국가유공자':[national_merit],
		'장애인':[disabled],
		'신규전입':[new],
		'한부모/조손':[single_parent],
		'확대가족':[many_family],
		'요양환자/치매환자':[alone_old_man],
		'취약계층':[vulnerable],
		'해당없음':[none_of_them],
		})
	total.append(d)
	result=pd.concat(total)
	file_name= 'user_arrange.csv'
	file_path=os.getcwd()+"/data/"
	result.to_csv(file_path+file_name,index=False,encoding='utf-8-sig')
	# print(file_name,'완료')
	return result

def word_arrange(user,selectfamily,selecttarget):
	total = []
	arr=[user.values()[0],selectfamily.values(),selecttarget.values()]
	print("user:: ",user.values())
	cur=arr[0]
	age09='@'
	age1019='@'
	age2029='@'
	age3039='@'
	age60='@'
	student='@'
	inoccupation='@'
	startup='@'
	farmerfisherman='@'
	smallcompony='@'
	job_defalut='@'
	child_ok='@'
	child_empty='@'
	female='@'
	male='@'
	not_have_house='@'
	pregnant='@'
	alone='@'
	other_culture='@'
	many_child='@'
	national_merit='@'
	disabled='@'
	new='@'
	single_parent='@'
	many_family='@'
	alone_old_man='@'
	vulnerable='@'
	none_of_them='@'  # 초기 값 설정
	
	# row=cur.iloc[j] #유저 한명
	id=int(cur['user_seq']) #유저 아이디
	row=cur['age']
	if row=='1':
		age09="아동"
	elif row=='2':
		age1019="청소년"
	elif row=='3':
		age2029="청년"
	elif row=='4':
		age3039="중장년"
	elif row=='5':
		age60="노년"
	elif row=='6':
		age09 = "아동"
		age1019 = "청소년"
		age2029 = "청년"
		age3039 = "중장년"
		age60 = "노년"
	# 연령대 끝
	row=cur['child']
	if row=='1':
		child_ok='자녀있음'
	elif row=='2':
		child_empty='자녀없음/상관없음'
	# 자녀유무 끝
	row=cur['female']
	if row==1:
		female='여성'
	row=cur['male']
	if row==1:
		male='남성'
	# user 데이터 끝 
	for l in range(1,len(arr)):
		welfare_data=arr[l] # selectfamily, selecttarget 데이터
		total_idx=len(welfare_data)
		# print("total_idx",total_idx)
		if(l==1): #selectfamily
			for j in range(total_idx):
				row=welfare_data[j]
				row=row['family_id']
				if(row==0):
					not_have_house = "무주택자"
				elif row == 1:
					pregnant = "임산부"
				elif row == 2:
					alone = "1인가구"
				elif row == 3:
					other_culture = "다문화/탈북민"
				elif row == 4:
					many_child = "다자녀"
				elif row == 5:
					national_merit = "보훈대상자/국가유공자"
				elif row == 6:
					disabled = "장애인"
				elif row == 7:
					new = "신규전입"
				elif row == 8:
					single_parent = "한부모/조손"
				elif row == 9:
					many_family = "확대가족"
				elif row == 10:
					alone_old_man = "요양환자/치매환자"
				elif row == 11:
					vulnerable = "취약계층"
				elif row == 12:
					none_of_them = "해당없음"
			# 가구 끝 
		if(l==2): #selecttarget
			for j in range(total_idx):
				row=welfare_data[j]
				row=row['target_id']
				if(row==0):
					student = "학생"
				elif row == 1:
					inoccupation = "무직"
				elif row == 2:
					startup = "창업"
				elif row == 3:
					farmerfisherman = "농어업인"
				elif row == 4:
					smallcompony = "중소기업"
				elif row == 5:
					job_defalut = "일반"
			# 대상 끝
	# 데이터 받기 완료        
	d=pd.DataFrame({
		'아동':[age09],
		'청소년':[age1019],
		'청년':[age2029],
		'중장년':[age3039],
		'노년':[age60],
		'학생':[student],
		'무직':[inoccupation],
		'창업':[startup],
		'농어업인':[farmerfisherman],
		'중소기업':[smallcompony],
		'일반':[job_defalut],
		'자녀여부 있음':[child_ok],
		'자녀여부 없음':[child_empty],
		'여성':[female],
		'남성':[male],
		'무주택자':[not_have_house],
		'임산부':[pregnant],
		'1인가구':[alone],
		'다문화/탈북민':[other_culture],
		'다자녀':[many_child],
		'보훈대상자/국가유공자':[national_merit],
		'장애인':[disabled],
		'신규전입':[new],
		'한부모/조손':[single_parent],
		'확대가족':[many_family],
		'요양환자/치매환자':[alone_old_man],
		'취약계층':[vulnerable],
		'해당없음':[none_of_them],
		})
	total.append(d)
	result=pd.concat(total)
	file_name= 'user_word_arrange.csv'
	file_path=os.getcwd()+"/data/"
	result.to_csv(file_path+file_name,index=False,encoding='utf-8-sig')
	# print(file_name,'완료')
	return result	

def user_vectorization(result):
	user_vector=csr_matrix(result, shape=None, dtype=None, copy=False)
	return user_vector

def user_group_mapping_dbscan(user_vector,user_seq,result_word):
	file_path = os.getcwd()+"/data/"
	full_welfare = pd.read_csv(file_path+'welfare+DBSCAN.csv')
	
	welfare_mean=[]
	# n번째 그룹만 뽑기
	#최소값과 최대값 구하기
	max_value=full_welfare['clustering'].max()
	min_value=full_welfare['clustering'].min()
	p={}
	for n in range(min_value,max_value+1):
		welfare= full_welfare.loc[(full_welfare.clustering==n)]
		welfare=welfare.iloc[:,3:31] #필요한 특성만 뽑기
		welfare_vector=csr_matrix(welfare, shape=None, dtype=None, copy=False) # 벡터화 
		genre_sim = cosine_similarity(user_vector, welfare_vector)
		df1 = pd.DataFrame(data=genre_sim)
		df1['mean'] = df1.mean(axis=1)
		welfare_mean.append(df1['mean'][0])
		p[n]=df1['mean'][0]
	# print("평균 리스트: ",welfare_mean)
	# print("가장 평균이 높은 그룹 : ", welfare_mean.index(max(welfare_mean))," , 평균:",max(welfare_mean))
	# max_group=welfare_mean.index(max(welfare_mean))
	print(p)
	p_sort=sorted(p.items(), key=lambda x: x[1], reverse=True)
	means=[]
	full_welfare_word = pd.read_csv(file_path+'welfare_word+DBSCAN.csv')
	x=result_word.values[0] # user 한명 단어특성 배열로
	x=[item for item in x if item != '@']
	# print("유저 특성,",x)
	# top3
	for n in range(5):
		welfare=full_welfare_word.loc[(full_welfare_word.clustering==p_sort[n][0])]
		welfare=welfare.iloc[:,3:31] #필요한 특성만 뽑기
		cnt=0
		for i in range(len(welfare)):
			y=welfare.values[i]
			y = [item for item in y if item != '@']
			# print(y)
			intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
			union_cardinality = len(set.union(*[set(x), set(y)]))
			# print(intersection_cardinality / float(union_cardinality))  
			# print(user.values[0])
			# print(welfare.values[0])
			cnt+=intersection_cardinality / float(union_cardinality)
		means.append(cnt/len(welfare))
	# print("최종 결과:", means)
	# print("가장 평균이 높은 그룹 : ", means.index(max(means)))
	print(p_sort[means.index(max(means))][0])
	max_group=p_sort[means.index(max(means))][0]
	user=User.objects.filter(user_seq=user_seq)
	user.update(user_group=max_group)


#---

# @api_view(['GET'])
# def insertusergroupAPI(request,user_seq):
# 	# user_seq=1; #유저 아이디 받아오기
# 	user=User.objects.filter(user_seq=user_seq);
# 	# print("user확인 :: ",user.values())
# 	#QuerySet()은 리스트이고, 객체는 dictionary 이므로 <variable name>[index]['key'] 의 형식으로 value값에 접근이 가능하다
# 	# print("user이름 :: ",user.values()[0]['username'])
# 	selectfamily=Selectfamily.objects.filter(user_seq=user_seq);
# 	selecttarget=Selecttarget.objects.filter(user_seq=user_seq);
# 	# print("selectfamily :: ",selectfamily.values())
# 	# print("selecttarget :: ",selecttarget.values())

# 	result=arrange(user,selectfamily,selecttarget)
# 	user_vector=user_vectorization(result)
# 	print(user_vector)
# 	# DBSCAN or Spherical K-Means
# 	user_group_mapping(user_vector,user_seq)

# 	return render(request,'user_info.html')

# def user_group_mapping(user_vector,user_seq):
# 	print("user_group_mapping")

# 	file_path = os.getcwd()+"/data/"
# 	full_welfare = pd.read_csv(file_path+'welfare+clustering.csv',)
	
# 	welfare_mean=[]
# 	# n번째 그룹만 뽑기
# 	# 20은 k의 개수 
# 	for n in range(20):
# 		welfare= full_welfare.loc[(full_welfare.clustering==n)]
# 		welfare=welfare.iloc[:,3:38] #필요한 특성만 뽑기
# 		# arr_select_welfare=[]
# 		# for i in range(len(tmp3)):
# 		#   row=tmp3.iloc[i] # 복지 혜택 한개
# 		#   ori_id=row[1] # welfare_id
# 		#   arr_select_welfare.append(ori_id)
# 		welfare_vector=csr_matrix(welfare, shape=None, dtype=None, copy=False) # 벡터화 
# 		genre_sim = cosine_similarity(user_vector, welfare_vector)
# 		df1 = pd.DataFrame(data=genre_sim)
# 		df1['mean'] = df1.mean(axis=1)
# 		# print(n,"번째 그룹 평균 : ",df1['mean'][0])
# 		welfare_mean.append(df1['mean'][0])
# 	print("가장 평균이 높은 그룹 : ", welfare_mean.index(max(welfare_mean)))
# 	max_group=welfare_mean.index(max(welfare_mean))
# 	user=User.objects.filter(user_seq=user_seq)
# 	user.update(user_group=max_group)