# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-22 13:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('name', models.CharField(max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '账号表',
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('addr', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='ClassList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_type', models.SmallIntegerField(choices=[(0, '面授（脱产）'), (1, '面授（周末）'), (2, '网络班')], verbose_name='课程类型')),
                ('semester', models.PositiveSmallIntegerField(verbose_name='学期')),
                ('start_date', models.DateField(verbose_name='开班日期')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='结业日期')),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Branch', verbose_name='校区')),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('price', models.PositiveSmallIntegerField()),
                ('period', models.PositiveSmallIntegerField(verbose_name='周期（月）')),
                ('outline', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CourseRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_num', models.PositiveSmallIntegerField(verbose_name='第几节（天）')),
                ('has_homework', models.BooleanField(default=True)),
                ('homework_title', models.CharField(blank=True, max_length=128, null=True)),
                ('homework_content', models.TextField(blank=True, null=True)),
                ('outline', models.TextField(verbose_name='本节课程大纲')),
                ('date', models.DateField(auto_now_add=True)),
                ('from_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ClassList', verbose_name='班级')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True)),
                ('qq', models.CharField(max_length=64, unique=True)),
                ('qq_name', models.CharField(blank=True, max_length=64, null=True)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('source', models.SmallIntegerField(choices=[(0, '转介绍'), (1, 'QQ群'), (2, '官网'), (3, '百度推广'), (4, '51CTO'), (5, '知乎'), (6, '市场推广')])),
                ('referral_from', models.CharField(blank=True, max_length=64, null=True, verbose_name='转介绍人qq')),
                ('content', models.TextField(verbose_name='咨询详情')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.SmallIntegerField(choices=[(0, '已报名'), (1, '未报名')], default=1)),
                ('consult_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course', verbose_name='咨询课程')),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='咨询专家')),
            ],
            options={
                'verbose_name': '客户表',
            },
        ),
        migrations.CreateModel(
            name='CustomerFollowUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='跟进内容')),
                ('intention', models.SmallIntegerField(choices=[(0, '2周内报名'), (1, '1个月内报名'), (2, '近期无报名计划'), (3, '已在其他机构报名'), (4, '已报名'), (5, '已拉黑')], verbose_name='报名意向')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='跟进人')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
            options={
                'verbose_name': '客户跟进表',
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_agree', models.BooleanField(default=False, verbose_name='学员已同意合同')),
                ('contract_approved', models.BooleanField(default=False, verbose_name='合同已审核')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='课程顾问')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
                ('enrolled_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ClassList', verbose_name='所报班级')),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('url_name', models.CharField(max_length=64)),
                ('url_type', models.SmallIntegerField(choices=[(0, '相对地址'), (1, '绝对路径')], default=0)),
            ],
            options={
                'verbose_name_plural': '菜单',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(default=500, verbose_name='缴费数额')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('consultant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='课程顾问')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course', verbose_name='所报课程')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('menus', models.ManyToManyField(blank=True, to='crm.Menu')),
            ],
            options={
                'verbose_name_plural': '角色',
            },
        ),
        migrations.CreateModel(
            name='StudyRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendence', models.SmallIntegerField(choices=[(0, '已签到'), (1, '迟到'), (2, '缺勤'), (3, '早退')], verbose_name='出勤记录')),
                ('score', models.SmallIntegerField(choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (75, 'B-'), (70, 'C+'), (60, 'C'), (40, 'C-'), (-50, 'D'), (-100, 'COPY'), (0, 'N/A')], default=0)),
                ('memo', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('date', models.DateField(auto_now_add=True)),
                ('course_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.CourseRecord')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Enrollment')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='crm.Tag', verbose_name='客户标签'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Course'),
        ),
        migrations.AddField(
            model_name='classlist',
            name='teachers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='studyrecord',
            unique_together=set([('student', 'course_record')]),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set([('customer', 'enrolled_class')]),
        ),
        migrations.AlterUniqueTogether(
            name='courserecord',
            unique_together=set([('from_class', 'day_num')]),
        ),
        migrations.AlterUniqueTogether(
            name='classlist',
            unique_together=set([('branch', 'course', 'semester')]),
        ),
    ]
