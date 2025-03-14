import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// URL base da API do backend
const String baseUrl = 'http://localhost:8000';

/// Função assíncrona que busca os hemocentros na API
Future<List<dynamic>> getHemocentros() async {
  final response = await http.get(Uri.parse('$baseUrl/hemocentros/'));

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Erro ao buscar hemocentros');
  }
}

void main() {
  runApp(DoeFacilApp());
}

/// Widget principal do aplicativo
class DoeFacilApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'DoeFácil',
      theme: ThemeData(
        primarySwatch: Colors.red, // Define o tema principal do app
      ),
      home: HomeScreen(), // Define a tela inicial
    );
  }
}

/// Tela inicial do aplicativo
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('DoeFácil')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              'Bem-vindo ao DoeFácil!',
              style: TextStyle(fontSize: 20),
            ),
            SizedBox(height: 20), // Espaço entre os elementos
            ElevatedButton(
              onPressed: () {
                // Ao pressionar o botão, vai para a tela de hemocentros
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => HemocentrosScreen()),
                );
              },
              child: Text('Encontrar Hemocentros'),
            ),
          ],
        ),
      ),
    );
  }
}

/// Tela que exibe a lista de hemocentros disponíveis
class HemocentrosScreen extends StatefulWidget {
  @override
  _HemocentrosScreenState createState() => _HemocentrosScreenState();
}

class _HemocentrosScreenState extends State<HemocentrosScreen> {
  List<dynamic> hemocentros = []; // Lista para armazenar os hemocentros

  @override
  void initState() {
    super.initState();
    fetchHemocentros();
  }

  /// Função para buscar os hemocentros da API
  void fetchHemocentros() async {
    try {
      var data = await getHemocentros();
      setState(() {
        hemocentros = data;
      });
    } catch (e) {
      print('Erro ao buscar hemocentros: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Hemocentros')),
      body: hemocentros.isEmpty
          ? Center(child: CircularProgressIndicator()) // Exibe um carregamento se os dados ainda não foram recebidos
          : ListView.builder(
              itemCount: hemocentros.length, // Número de itens na lista
              itemBuilder: (context, index) {
                return ListTile(
                  title: Text(hemocentros[index]['nome']), // Nome do hemocentro
                  subtitle: Text(hemocentros[index]['endereco']), // Endereço do hemocentro
                );
              },
            ),
    );
  }
}
