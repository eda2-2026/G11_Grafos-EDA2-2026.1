import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from graph import NetworkGraph

st.set_page_config(page_title="Simulador de Redes - Teoria dos Grafos", layout="wide")

# Inicializa o grafo na sessão
if 'network' not in st.session_state:
    st.session_state.network = NetworkGraph()

network = st.session_state.network

# Dicionário de cores por tipo de dispositivo
DEVICE_COLORS = {
    "Servidor": "#ff9999",
    "Roteador": "#ffcc99",
    "Switch": "#99ff99",
    "PC": "#99ccff",
    "Notebook": "#cc99ff",
    "Impressora": "#ffff99",
    "Outro": "#e0e0e0"
}

def draw_network(path=None):
    # Cria o grafo no NetworkX APENAS para visualização
    G = nx.Graph()
    
    devices = network.get_devices()
    for dev in devices:
        G.add_node(dev, type=network.nodes[dev]["type"])
        
    connections = network.get_connections()
    for u, v in connections:
        G.add_edge(u, v)

    if not G.nodes:
        return None

    pos = nx.spring_layout(G, seed=42)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Desenha nós
    node_colors = [DEVICE_COLORS.get(G.nodes[n]["type"], DEVICE_COLORS["Outro"]) for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=ax)
    
    # Desenha labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
    
    # Desenha arestas normais
    nx.draw_networkx_edges(G, pos, edge_color="gray", ax=ax)
    
    # Se houver um caminho (BFS), destaca as arestas
    if path and len(path) > 1:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=3, ax=ax)
        # Destaca nós do caminho
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="gold", node_size=1000, ax=ax)

    ax.axis("off")
    return fig

# ======== INTERFACE ========

st.title("🌐 Simulador de Redes de Computadores")
st.markdown("Aplicação prática da **Teoria dos Grafos** para análise de conectividade de redes. Os algoritmos (BFS, DFS, Componentes Conectadas) são implementados manualmente.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Gerenciamento")
    
    # Cadastro de Dispositivos
    st.subheader("Cadastrar Dispositivo")
    with st.form("add_device_form"):
        dev_name = st.text_input("Nome do Dispositivo (ex: PC-01)")
        dev_type = st.selectbox("Tipo", list(DEVICE_COLORS.keys()))
        submit_dev = st.form_submit_button("Adicionar")
        if submit_dev and dev_name:
            network.add_device(dev_name, dev_type)
            st.rerun()

    # Criação de Conexões
    st.subheader("Conectar Dispositivos")
    devices_list = network.get_devices()
    with st.form("add_conn_form"):
        if len(devices_list) >= 2:
            dev1 = st.selectbox("Dispositivo 1", devices_list, key="conn_d1")
            dev2 = st.selectbox("Dispositivo 2", devices_list, key="conn_d2")
            submit_conn = st.form_submit_button("Conectar")
            if submit_conn and dev1 != dev2:
                network.add_connection(dev1, dev2)
                st.rerun()
        else:
            st.warning("Adicione pelo menos 2 dispositivos.")
            st.form_submit_button("Conectar", disabled=True)

    # Simulação de Falhas / Remoção
    st.subheader("Simular Falhas (Remover)")
    remove_tab1, remove_tab2 = st.tabs(["Dispositivo", "Conexão"])
    
    with remove_tab1:
        with st.form("remove_dev_form"):
            if devices_list:
                dev_to_rem = st.selectbox("Remover Dispositivo", devices_list)
                if st.form_submit_button("Remover Dispositivo"):
                    network.remove_device(dev_to_rem)
                    st.rerun()
            else:
                st.info("Nenhum dispositivo na rede.")
                st.form_submit_button("Remover Dispositivo", disabled=True)
                
    with remove_tab2:
        with st.form("remove_conn_form"):
            conns = network.get_connections()
            if conns:
                conn_strs = [f"{u} <-> {v}" for u, v in conns]
                conn_to_rem = st.selectbox("Remover Conexão", conn_strs)
                if st.form_submit_button("Remover Conexão"):
                    idx = conn_strs.index(conn_to_rem)
                    u, v = conns[idx]
                    network.remove_connection(u, v)
                    st.rerun()
            else:
                st.info("Nenhuma conexão na rede.")
                st.form_submit_button("Remover Conexão", disabled=True)

with col2:
    st.header("Visualização e Análise")
    
    # Estatísticas
    components = network.connected_components()
    num_nodes = len(network.get_devices())
    num_edges = len(network.get_connections())
    
    met1, met2, met3 = st.columns(3)
    met1.metric("Dispositivos (Vértices)", num_nodes)
    met2.metric("Conexões (Arestas)", num_edges)
    met3.metric("Componentes Conectadas", len(components))
    
    if len(components) > 1:
        st.error(f"⚠️ Alerta: A rede está dividida em {len(components)} partes isoladas!")
    elif len(components) == 1:
        st.success("✅ A rede está totalmente conectada!")
    else:
        st.info("A rede está vazia.")

    # Algoritmos
    st.subheader("Algoritmos de Grafos")
    algo_tab1, algo_tab2 = st.tabs(["Busca em Largura (BFS)", "Busca em Profundidade (DFS)"])
    
    path_to_draw = None

    with algo_tab1:
        st.markdown("**Objetivo:** Encontrar um caminho entre dois dispositivos e ver a ordem de visita.")
        if len(devices_list) >= 2:
            col_bfs1, col_bfs2 = st.columns(2)
            with col_bfs1:
                bfs_start = st.selectbox("Origem", devices_list, key="bfs_start")
            with col_bfs2:
                bfs_target = st.selectbox("Destino", devices_list, key="bfs_target")
                
            if st.button("Executar BFS"):
                path, visit_order = network.bfs(bfs_start, bfs_target)
                st.write(f"**Ordem de Visita (BFS):** {' -> '.join(visit_order)}")
                
                if path:
                    st.write(f"**Caminho Encontrado:** {' -> '.join(path)}")
                    path_to_draw = path
                    st.success("Caminho encontrado e destacado na visualização!")
                else:
                    st.error("Nenhum caminho encontrado entre os dispositivos (eles estão em componentes diferentes).")
        else:
            st.info("Necessário pelo menos 2 dispositivos.")

    with algo_tab2:
        st.markdown("**Objetivo:** Percorrer todos os dispositivos alcançáveis a partir de uma origem.")
        if devices_list:
            dfs_start = st.selectbox("Origem", devices_list, key="dfs_start")
            if st.button("Executar DFS"):
                visit_order = network.dfs(dfs_start)
                st.write(f"**Ordem de Visita (DFS):** {' -> '.join(visit_order)}")
                st.info(f"Foram alcançados {len(visit_order)} dispositivos a partir de {dfs_start}.")
        else:
            st.info("Nenhum dispositivo na rede.")

    # Desenho do Grafo
    st.subheader("Topologia da Rede")
    fig = draw_network(path_to_draw)
    if fig:
        st.pyplot(fig)
    else:
        st.info("Adicione dispositivos para visualizar a rede.")
