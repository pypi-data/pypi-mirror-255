# coding=utf-8
from setuptools import setup,find_packages
setup(name='bodies-sr',
      version='1.0.1',
      description='run the threebodies',
      author='Riming',
      author_email='dhjfirst@hotmail.com',
      requires= ['numpy'], # ����������Щģ��
      packages=find_packages(),  # ϵͳ�Զ��ӵ�ǰĿ¼��ʼ�Ұ�
      # ����е��ļ����ô������ֻ��ָ����Ҫ������ļ�
      #packages=['����1','����2','__init__']  #ָ��Ŀ¼����Ҫ�����py�ļ���ע�ⲻҪ.py��׺
      license="apache 3.0"
      )

