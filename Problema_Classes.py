#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Importação das funções do gurobi
from gurobipy import*
from math import*

class Problema(object):
    def __init__(self, nomeArquivo):
        #Leitura do arquivo
        self.arquivo = open(nomeArquivo, 'r')
        tamanhoGrafo = self.arquivo.readline()
        str = tamanhoGrafo.split()
        self.numVertice = int(str[0])
        self.numAresta = int(str[1])

        #Matrizes do problema
        self.matrizAdjacencia = [[0 for i in range(self.numVertice+1)] for j in range(self.numVertice +1)]
        self.matrizDistancia = [[0 for i in range(self.numVertice+1)] for j in range(self.numVertice +1)]
        self.matrizCusto = [[0.0 for i in range(self.numVertice+1)] for j in range(self.numVertice +1)]

        #Leitura das linhas e preenchimento das matrizes
        for i in range(1, self.numAresta +1):
            str = self.arquivo.readline()
            str = str.split()
            origem = int(str[0])
            destino = int(str[1])
            distancia = int(str[2])
            custo = float(str[3])
            self.matrizAdjacencia[origem][destino] = 1
            self.matrizAdjacencia[destino][origem] = 1			#mexi aqui
            self.matrizDistancia[origem][destino] = distancia
            self.matrizDistancia[destino][origem] = distancia
            self.matrizCusto[origem][destino] = custo
            self.matrizCusto[destino][origem] = custo

        self.arquivo.close()

    #Exibe informacoes do grafo
    def mostraGrafo(self):
        print("%d %d " % (self.numVertice, self.numAresta))
        for i in range(1, self.numVertice+1):
            for j in range(1, self.numVertice+1):
            	if self.matrizAdjacencia[i][j] == 1:
                	print("%d %d %d %f" % (i, j, self.matrizDistancia[i][j], self.matrizCusto[i][j]))

    #Buscas
    def buscaAdjacencia(self, origem, destino):
    	return self.matrizAdjacencia[origem][destino]

    def buscaDistancia(self, origem, destino):
        return self.matrizDistancia[origem][destino]

    def buscaCusto(self, origem, destino):
        return self.matrizCusto[origem][destino]

##########################################################
problema = Problema("jm_final.txt")

vertices = problema.numVertice
matrizAdjacencia = problema.matrizAdjacencia
matrizDistancia = problema.matrizDistancia
matrizCusto = problema.matrizCusto
print "Vertices: = ", vertices

#Criando um modelo vazio
model = Model("coletaRSD")
x,l,f = {},{},{}
veiculos = 2


#Criação das variáveis de decisão	
for i in range(1,vertices+1):
	for j in range(1,vertices+1):
		for p in range(1,veiculos+1):
			if(matrizAdjacencia[i][j] == 1):			
				x[i,j,p] = model.addVar(obj = matrizDistancia[i][j],vtype = GRB.BINARY, name = "x[%s,%s,%s]"%(i,j,p))
				l[i,j,p] = model.addVar(obj = 0,vtype = GRB.BINARY, name = "l[%s,%s,%s]"%(i,j,p))
				f[i,j,p] = model.addVar(lb = 0, ub = GRB.INFINITY, obj = 0,vtype = GRB.INTEGER, name = "f[%s,%s,%s]"%(i,j,p))

model.update()
#Definição da Função Objetivo


#Adição das Restrições

#Restrição 1

for i in range(1,	 vertices + 1):
	for p in range(1, veiculos + 1):
		var = []
		coef = []
		for k in range(1, vertices + 1):
			if (matrizAdjacencia[k][i] == 1):
				coef.append(1)
				var.append(x[k,i,p])
			if (matrizAdjacencia[k][i] == 1):
				coef.append(-1)
				var.append(x[i,k,p])
		model.addConstr(LinExpr(coef, var),"=",0,name="R1[%s][%s]"%(i,p))

#Restrição 2

w = 15000 #Capacidade dos veículos em quilos

for i in range(1, vertices + 1):
	for j in range(1, vertices + 1):
		var2 = []
		coef2 = []
		aux = 0
		for p in range(1, veiculos + 1):
			if(matrizAdjacencia[i][j] == 1):
			#teto de Qij/w
				aux = ceil(matrizCusto[i][j]/w)
				coef2.append(1)
				var2.append(l[i,j,p])
			#if(matrizAdjacencia[j][i] == 1):	
				coef2.append(1)
				var2.append(l[j,i,p])				
		model.addConstr(LinExpr(coef2, var2),"=",aux,name="R2[%s][%s]"%(i,j))

#Restrição 3

for p in range(1, veiculos + 1):
	for i in range(1, vertices + 1):
		for j in range(1, vertices + 1):
			if(matrizAdjacencia[i][j] == 1):
				model.addConstr(x[i,j,p],">=",l[i,j,p],name="R3[%s][%s][%s]"%(p,i,j)) 

#Restrição 4

for p in range(1, veiculos + 1):
	var3 = []
	coef3 = []
	for i in range(1, vertices + 1):
		for j in range(1, vertices + 1):
			#if(matrizAdjacencia[i][j] == 1):
			coef3.append(matrizCusto[i][j])
			var3.append(l[i,j,p])
	model.addConstr(LinExpr(coef3, var3),"<=",w,name="R4[%s]"%(p))

#Restrição 5

i = 2
while i <= vertices:
	for p in range(1, veiculos + 1):
		var = []
		coef = []
		for k in range(1, vertices + 1):
			if(matrizAdjacencia[i][k] == 1):
				coef.append(1)
				var.append(f[i,k,p])
			if(matrizAdjacencia[k][i] == 1):
				coef.append(-1)
				var.append(f[k,i,p])
			if (matrizAdjacencia[i][k]):
				coef.append(-1)
				var.append(l[i,k,p])
		model.addConstr(LinExpr(coef, var),"=",0,name="R5[%s][%s]"%(i,p))
	i = i +1


for p in range(1, veiculos + 1):
	for i in range(1, vertices + 1):
		for j in range(1, vertices + 1):
			if(matrizAdjacencia[i][j] == 1):
				n2 = pow(vertices,2)
				aux = n2*x[i,j,p]

				model.addConstr(aux,">=",f[i,j,p],name="R5'[%s][%s,%s]"%(p,i,j))

#Atualiza modelo
model.update()

#Otimiza modelo
model.optimize()

#Print na solução

solucao = model.getAttr('X',x)

for i in range(1, vertices + 1):

	for j in range(1, vertices + 1):
		for p in range(1, veiculos + 1):
				if (solucao[i,j,p] == 1):
					 print  "Aresta[%s][%s] Caminhão %s"%(i,j,p)			
					 
	
#Escrevendo arquivo do modelo
model.write("coletaRSD.lp")
