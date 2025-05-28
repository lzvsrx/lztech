// main.dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:crypto/crypto.dart'; // Para hashing

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LZTech Chatbot',
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.blueGrey,
          foregroundColor: Colors.white,
          elevation: 0,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.blueGrey,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.grey[200],
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
        cardTheme: CardTheme(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const AuthScreen(),
    );
  }
}

// Função para criptografar senha usando SHA256
String hashPassword(String password) {
  var bytes = utf8.encode(password); // Converte a string para bytes
  var digest = sha256.convert(bytes); // Criptografa
  return digest.toString(); // Retorna o hash como string
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  String _authAction = 'Login'; // 'Login' ou 'Cadastrar'

  // Função para lidar com login/cadastro
  Future<void> _handleAuth() async {
    final username = _usernameController.text;
    final password = _passwordController.text;

    if (username.isEmpty || password.isEmpty) {
      _showMessage('Por favor, preencha usuário e senha.');
      return;
    }

    final hashedPassword = hashPassword(password);
    final prefs = await SharedPreferences.getInstance();
    final userDataJson = prefs.getString('user_data_$username');

    if (_authAction == 'Cadastrar') {
      if (userDataJson != null) {
        _showMessage('Usuário já existe.');
      } else {
        final userData = {'senha': hashedPassword, 'valores': []};
        await prefs.setString('user_data_$username', jsonEncode(userData));
        _showMessage('Cadastro realizado com sucesso! Faça login agora.');
        setState(() {
          _authAction = 'Login'; // Mudar para login após o cadastro
        });
      }
    } else {
      // Login
      if (userDataJson == null) {
        _showMessage('Usuário não encontrado.');
        return;
      }
      final userData = jsonDecode(userDataJson);
      if (userData['senha'] == hashedPassword) {
        // Navegar para a tela principal
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (context) => MainScreen(username: username),
          ),
        );
      } else {
        _showMessage('Senha incorreta.');
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🤖 LZTech Chatbot'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '📅 Data: ${DateTime.now().day}/${DateTime.now().month}/${DateTime.now().year}',
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 30),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                    Text(
                      '🔐 Login ou Cadastro',
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 20),
                    TextField(
                      controller: _usernameController,
                      decoration: const InputDecoration(
                        labelText: 'Usuário',
                        prefixIcon: Icon(Icons.person),
                      ),
                    ),
                    const SizedBox(height: 15),
                    TextField(
                      controller: _passwordController,
                      decoration: const InputDecoration(
                        labelText: 'Senha',
                        prefixIcon: Icon(Icons.lock),
                      ),
                      obscureText: true,
                    ),
                    const SizedBox(height: 20),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        ChoiceChip(
                          label: const Text('Login'),
                          selected: _authAction == 'Login',
                          onSelected: (selected) {
                            setState(() {
                              _authAction = selected ? 'Login' : 'Cadastrar';
                            });
                          },
                          selectedColor: Theme.of(context).primaryColor,
                          labelStyle: TextStyle(color: _authAction == 'Login' ? Colors.white : Colors.black),
                        ),
                        ChoiceChip(
                          label: const Text('Cadastrar'),
                          selected: _authAction == 'Cadastrar',
                          onSelected: (selected) {
                            setState(() {
                              _authAction = selected ? 'Cadastrar' : 'Login';
                            });
                          },
                          selectedColor: Theme.of(context).primaryColor,
                          labelStyle: TextStyle(color: _authAction == 'Cadastrar' ? Colors.white : Colors.black),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _handleAuth,
                      child: Text(_authAction),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  final String username;
  const MainScreen({super.key, required this.username});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  List<double> _valores = [];
  final TextEditingController _newValueController = TextEditingController();
  String _currentAction = 'Adicionar valor'; // Ação padrão

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  // Carrega os dados do usuário
  Future<void> _loadUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataJson = prefs.getString('user_data_${widget.username}');
    if (userDataJson != null) {
      final userData = jsonDecode(userDataJson);
      setState(() {
        _valores = (userData['valores'] as List).map((e) => e as double).toList();
      });
    }
  }

  // Salva os dados do usuário
  Future<void> _saveUserData() async {
    final prefs = await SharedPreferences.getInstance();
    final userDataJson = prefs.getString('user_data_${widget.username}');
    if (userDataJson != null) {
      final userData = jsonDecode(userDataJson);
      userData['valores'] = _valores;
      await prefs.setString('user_data_${widget.username}', jsonEncode(userData));
    }
  }

  // Adiciona um novo valor
  void _addValue() {
    final value = double.tryParse(_newValueController.text);
    if (value == null) {
      _showMessage('Por favor, digite um valor numérico válido.');
      return;
    }
    setState(() {
      _valores.add(value);
    });
    _saveUserData();
    _newValueController.clear();
    _showMessage('Valor $value adicionado com sucesso!');
  }

  // Limpa todos os dados
  void _clearData() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Confirmar Limpeza'),
          content: const Text('Tem certeza que deseja limpar todos os dados?'),
          actions: <Widget>[
            TextButton(
              child: const Text('Cancelar'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: const Text('Limpar'),
              onPressed: () {
                setState(() {
                  _valores = [];
                });
                _saveUserData();
                _showMessage('Todos os dados foram removidos.');
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  // Calcula a soma total
  double _getTotalSum() {
    return _valores.fold(0.0, (sum, item) => sum + item);
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Bem-vindo, ${widget.username}!'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const AuthScreen()),
              );
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Ações disponíveis:',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8.0, // Espaçamento horizontal entre os botões
              runSpacing: 4.0, // Espaçamento vertical entre as linhas de botões
              children: [
                _buildActionButton('Adicionar valor'),
                _buildActionButton('Ver todos os dados'),
                _buildActionButton('Ver a soma total'),
                _buildActionButton('Limpar dados'),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: _buildCurrentActionView(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(String action) {
    return ChoiceChip(
      label: Text(action),
      selected: _currentAction == action,
      onSelected: (selected) {
        setState(() {
          _currentAction = action;
        });
      },
      selectedColor: Theme.of(context).primaryColor,
      labelStyle: TextStyle(color: _currentAction == action ? Colors.white : Colors.black87),
    );
  }

  Widget _buildCurrentActionView() {
    switch (_currentAction) {
      case 'Adicionar valor':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Adicionar valor:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            TextField(
              controller: _newValueController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Digite um valor numérico',
                prefixIcon: Icon(Icons.attach_money),
              ),
            ),
            const SizedBox(height: 15),
            ElevatedButton(
              onPressed: _addValue,
              child: const Text('Adicionar'),
            ),
          ],
        );
      case 'Ver todos os dados':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Valores armazenados:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            if (_valores.isEmpty)
              const Text('Nenhum valor armazenado ainda.', style: TextStyle(fontStyle: FontStyle.italic))
            else
              Expanded(
                child: ListView.builder(
                  itemCount: _valores.length,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Text('- ${_valores[index].toStringAsFixed(2)}', style: const TextStyle(fontSize: 16)),
                    );
                  },
                ),
              ),
          ],
        );
      case 'Ver a soma total':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Soma total dos dados:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            Text(
              _getTotalSum().toStringAsFixed(2),
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.blueGrey),
            ),
          ],
        );
      case 'Limpar dados':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Limpar dados:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            ElevatedButton.icon(
              onPressed: _clearData,
              icon: const Icon(Icons.delete_forever),
              label: const Text('Confirmar limpeza dos dados'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            ),
          ],
        );
      default:
        return const Center(child: Text('Selecione uma ação.'));
    }
  }
}
