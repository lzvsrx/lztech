// App.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  Button,
  StyleSheet,
  ScrollView,
  Alert,
  TouchableOpacity,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Crypto from 'expo-crypto'; // Usaremos Expo Crypto para hashing, ou uma implementação simples

// Função para criptografar senha (usando uma implementação simples para demonstração)
// Em um ambiente de produção, use uma biblioteca de hashing mais robusta e segura.
const hashPassword = async (password) => {
  // Para um ambiente real, você usaria uma biblioteca como 'react-native-sha256'
  // ou 'expo-crypto' se estiver usando Expo.
  // Exemplo com Expo Crypto:
  if (Crypto.digestString) {
    return await Crypto.digestString(
      Crypto.CryptoDigestAlgorithm.SHA256,
      password,
      { encoding: Crypto.CryptoEncoding.HEX }
    );
  } else {
    // Fallback simples para demonstração se Expo Crypto não estiver disponível
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
      const char = password.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash |= 0; // Converte para um inteiro de 32 bits
    }
    return hash.toString(16);
  }
};

const App = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [action, setAction] = useState('Login'); // 'Login' ou 'Cadastrar'
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState({ senha: '', valores: [] });
  const [newValue, setNewValue] = useState('');
  const [currentAction, setCurrentAction] = useState('Adicionar valor'); // Ação principal após login

  // Efeito para carregar dados do usuário ao iniciar ou mudar de usuário
  useEffect(() => {
    if (username) {
      loadUserData();
    } else {
      setUserData({ senha: '', valores: [] });
      setIsLoggedIn(false);
    }
  }, [username]);

  // Função para carregar dados do usuário do AsyncStorage
  const loadUserData = async () => {
    try {
      const jsonValue = await AsyncStorage.getItem(`@user_data_${username}`);
      if (jsonValue != null) {
        setUserData(JSON.parse(jsonValue));
      } else {
        setUserData({ senha: '', valores: [] });
      }
    } catch (e) {
      Alert.alert('Erro', 'Falha ao carregar dados do usuário.');
      console.error(e);
    }
  };

  // Função para salvar dados do usuário no AsyncStorage
  const saveUserData = async (data) => {
    try {
      const jsonValue = JSON.stringify(data);
      await AsyncStorage.setItem(`@user_data_${username}`, jsonValue);
      setUserData(data); // Atualiza o estado local também
    } catch (e) {
      Alert.alert('Erro', 'Falha ao salvar dados do usuário.');
      console.error(e);
    }
  };

  // Lida com o login e cadastro
  const handleAuth = async () => {
    if (!username || !password) {
      Alert.alert('Erro', 'Por favor, preencha usuário e senha.');
      return;
    }

    const hashedPassword = await hashPassword(password);
    const existingUserData = await AsyncStorage.getItem(`@user_data_${username}`);

    if (action === 'Cadastrar') {
      if (existingUserData != null) {
        Alert.alert('Erro', 'Usuário já existe.');
      } else {
        const newUser = { senha: hashedPassword, valores: [] };
        await saveUserData(newUser);
        Alert.alert('Sucesso', 'Cadastro realizado com sucesso!');
        setAction('Login'); // Sugere login após cadastro
      }
    } else { // Login
      if (existingUserData == null) {
        Alert.alert('Erro', 'Usuário não encontrado.');
        return;
      }
      const parsedData = JSON.parse(existingUserData);
      if (parsedData.senha === hashedPassword) {
        setUserData(parsedData);
        setIsLoggedIn(true);
        Alert.alert('Sucesso', `Bem-vindo, ${username}!`);
      } else {
        Alert.alert('Erro', 'Senha incorreta.');
      }
    }
  };

  // Lida com a adição de um novo valor
  const handleAddValue = async () => {
    const value = parseFloat(newValue);
    if (isNaN(value)) {
      Alert.alert('Erro', 'Por favor, digite um valor numérico válido.');
      return;
    }
    const updatedData = { ...userData, valores: [...userData.valores, value] };
    await saveUserData(updatedData);
    setNewValue('');
    Alert.alert('Sucesso', `Valor ${value} adicionado.`);
  };

  // Lida com a limpeza dos dados
  const handleClearData = async () => {
    Alert.alert(
      'Confirmar',
      'Tem certeza que deseja limpar todos os dados?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Limpar',
          onPress: async () => {
            const updatedData = { ...userData, valores: [] };
            await saveUserData(updatedData);
            Alert.alert('Sucesso', 'Todos os dados foram removidos.');
          },
        },
      ],
      { cancelable: true }
    );
  };

  // Calcula a soma total dos valores
  const getTotalSum = () => {
    return userData.valores.reduce((sum, val) => sum + val, 0);
  };

  // Renderiza a tela de autenticação
  const renderAuthScreen = () => (
    <View style={styles.authContainer}>
      <Text style={styles.header}>🔐 Login ou Cadastro</Text>
      <TextInput
        style={styles.input}
        placeholder="Usuário"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      <TextInput
        style={styles.input}
        placeholder="Senha"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      <View style={styles.radioContainer}>
        <TouchableOpacity
          style={[styles.radioButton, action === 'Login' && styles.radioButtonSelected]}
          onPress={() => setAction('Login')}
        >
          <Text style={styles.radioText}>Login</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.radioButton, action === 'Cadastrar' && styles.radioButtonSelected]}
          onPress={() => setAction('Cadastrar')}
        >
          <Text style={styles.radioText}>Cadastrar</Text>
        </TouchableOpacity>
      </View>
      <Button title={action} onPress={handleAuth} />
    </View>
  );

  // Renderiza a tela principal após o login
  const renderMainScreen = () => (
    <ScrollView style={styles.mainContainer}>
      <Text style={styles.welcomeText}>Bem-vindo, {username}!</Text>
      <Text style={styles.sectionTitle}>Ações disponíveis:</Text>
      <View style={styles.actionButtonsContainer}>
        {['Adicionar valor', 'Ver todos os dados', 'Ver a soma total', 'Limpar dados'].map((act) => (
          <TouchableOpacity
            key={act}
            style={[styles.actionButton, currentAction === act && styles.actionButtonSelected]}
            onPress={() => setCurrentAction(act)}
          >
            <Text style={styles.actionButtonText}>{act}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {currentAction === 'Adicionar valor' && (
        <View style={styles.actionSection}>
          <Text style={styles.sectionSubtitle}>Adicionar valor:</Text>
          <TextInput
            style={styles.input}
            placeholder="Digite um valor numérico"
            keyboardType="numeric"
            value={newValue}
            onChangeText={setNewValue}
          />
          <Button title="Adicionar" onPress={handleAddValue} />
        </View>
      )}

      {currentAction === 'Ver todos os dados' && (
        <View style={styles.actionSection}>
          <Text style={styles.sectionSubtitle}>Valores armazenados:</Text>
          {userData.valores.length > 0 ? (
            userData.valores.map((val, index) => (
              <Text key={index} style={styles.dataItem}>- {val}</Text>
            ))
          ) : (
            <Text style={styles.infoText}>Nenhum valor armazenado ainda.</Text>
          )}
        </View>
      )}

      {currentAction === 'Ver a soma total' && (
        <View style={styles.actionSection}>
          <Text style={styles.sectionSubtitle}>Soma total dos dados:</Text>
          <Text style={styles.totalSumText}>{getTotalSum()}</Text>
        </View>
      )}

      {currentAction === 'Limpar dados' && (
        <View style={styles.actionSection}>
          <Button title="Limpar Dados" color="red" onPress={handleClearData} />
        </View>
      )}

      <Button title="Sair" onPress={() => setIsLoggedIn(false)} style={styles.logoutButton} />
    </ScrollView>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.appTitle}>🤖 LZTech Chatbot</Text>
      <Text style={styles.dateText}>📅 Data: {new Date().toLocaleDateString('pt-BR')}</Text>
      {isLoggedIn ? renderMainScreen() : renderAuthScreen()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
    padding: 20,
    paddingTop: 50, // Ajuste para evitar a barra de status
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 5,
  },
  dateText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  authContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  header: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#444',
  },
  input: {
    width: '100%',
    height: 50,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 15,
    marginBottom: 15,
    backgroundColor: '#f9f9f9',
    fontSize: 16,
  },
  radioContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginBottom: 20,
  },
  radioButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#007bff',
    backgroundColor: '#e9f5ff',
  },
  radioButtonSelected: {
    backgroundColor: '#007bff',
  },
  radioText: {
    color: '#007bff',
    fontWeight: 'bold',
  },
  mainContainer: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#555',
    marginBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 5,
  },
  actionButtonsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  actionButton: {
    backgroundColor: '#6c757d',
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 25,
    margin: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 3,
  },
  actionButtonSelected: {
    backgroundColor: '#28a745', // Cor verde para a ação selecionada
  },
  actionButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  actionSection: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e2e6ea',
  },
  sectionSubtitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 10,
    color: '#495057',
  },
  dataItem: {
    fontSize: 16,
    paddingVertical: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    color: '#343a40',
  },
  infoText: {
    fontSize: 16,
    color: '#777',
    textAlign: 'center',
    paddingVertical: 10,
  },
  totalSumText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007bff',
    textAlign: 'center',
    paddingVertical: 10,
  },
  logoutButton: {
    marginTop: 20,
  },
});

export default App;
