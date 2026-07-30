import EvolutionModel as evo

args = evo.args
initial_list = evo.initial_list
srates = args.pop("srates")

print("# Args")
for item in args.items():
    print(">>",item[0],":",item[1])
print()

evo.show_gene_count(initial_list,10)
if len(srates)!=0:
    evo.graph(srates)








