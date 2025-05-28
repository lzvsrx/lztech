// MainActivity.kt
package com.lztech.chatbot

import android.content.Context
import android.content.SharedPreferences
import android.os.Bundle
import android.security.MessageDigest
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.nio.charset.StandardCharsets
import java.security.NoSuchAlgorithmException
import java.util.Date

class MainActivity : AppCompatActivity() {

    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var gson: Gson

    // Views de autenticação
    private lateinit var authLayout: LinearLayout
    private lateinit var etUsernameAuth: EditText
    private lateinit var etPasswordAuth: EditText
    private lateinit var rgAction: RadioGroup
    private lateinit var rbLogin: RadioButton
    private lateinit var rbRegister: RadioButton
    private lateinit var btnAuth: Button

    // Views da tela principal
    private lateinit var mainLayout: LinearLayout
    private lateinit var tvWelcome: TextView
    private lateinit var tvDate: TextView
    private lateinit var btnAddValue: Button
    private lateinit var btnViewData: Button
    private lateinit var btnSumTotal: Button
    private lateinit var btnClearData: Button
    private lateinit var btnLogout: Button

    // Seções de ação
    private lateinit var addValueSection: LinearLayout
    private lateinit var etNewValue: EditText
    private lateinit var btnConfirmAddValue: Button

    private lateinit var viewDataSection: LinearLayout
    private lateinit var tvStoredValues: TextView

    private lateinit var sumTotalSection: LinearLayout
    private lateinit var tvTotalSum: TextView

    private lateinit var clearDataSection: LinearLayout
    private lateinit var btnConfirmClearData: Button


    private var currentUsername: String = ""
    private var currentUserData: UserData = UserData("", mutableListOf())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sharedPreferences = getSharedPreferences("LZTechChatbotPrefs", Context.MODE_PRIVATE)
        gson = Gson()

        // Inicializa as views
        initViews()
        updateDateDisplay() // Atualiza a data ao iniciar

        // Define listeners
        setupListeners()

        // Inicialmente, mostra a tela de autenticação
        showAuthScreen()
    }

    private fun initViews() {
        // Autenticação
        authLayout = findViewById(R.id.auth_layout)
        etUsernameAuth = findViewById(R.id.et_username_auth)
        etPasswordAuth = findViewById(R.id.et_password_auth)
        rgAction = findViewById(R.id.rg_action)
        rbLogin = findViewById(R.id.rb_login)
        rbRegister = findViewById(R.id.rb_register)
        btnAuth = findViewById(R.id.btn_auth)

        // Principal
        mainLayout = findViewById(R.id.main_layout)
        tvWelcome = findViewById(R.id.tv_welcome)
        tvDate = findViewById(R.id.tv_date)
        btnAddValue = findViewById(R.id.btn_add_value)
        btnViewData = findViewById(R.id.btn_view_data)
        btnSumTotal = findViewById(R.id.btn_sum_total)
        btnClearData = findViewById(R.id.btn_clear_data)
        btnLogout = findViewById(R.id.btn_logout)

        // Seções de ação
        addValueSection = findViewById(R.id.add_value_section)
        etNewValue = findViewById(R.id.et_new_value)
        btnConfirmAddValue = findViewById(R.id.btn_confirm_add_value)

        viewDataSection = findViewById(R.id.view_data_section)
        tvStoredValues = findViewById(R.id.tv_stored_values)

        sumTotalSection = findViewById(R.id.sum_total_section)
        tvTotalSum = findViewById(R.id.tv_total_sum)

        clearDataSection = findViewById(R.id.clear_data_section)
        btnConfirmClearData = findViewById(R.id.btn_confirm_clear_data)
    }

    private fun setupListeners() {
        btnAuth.setOnClickListener { handleAuth() }
        btnLogout.setOnClickListener { showAuthScreen() }

        btnAddValue.setOnClickListener { showActionSection(addValueSection) }
        btnViewData.setOnClickListener { showActionSection(viewDataSection); displayStoredValues() }
        btnSumTotal.setOnClickListener { showActionSection(sumTotalSection); displayTotalSum() }
        btnClearData.setOnClickListener { showActionSection(clearDataSection) }

        btnConfirmAddValue.setOnClickListener { addValue() }
        btnConfirmClearData.setOnClickListener { confirmClearData() }
    }

    private fun updateDateDisplay() {
        val currentDate = Date()
        val formattedDate = android.text.format.DateFormat.format("dd/MM/yyyy", currentDate).toString()
        tvDate.text = "📅 Data: $formattedDate"
    }

    private fun showAuthScreen() {
        authLayout.visibility = View.VISIBLE
        mainLayout.visibility = View.GONE
        etUsernameAuth.setText("")
        etPasswordAuth.setText("")
        rbLogin.isChecked = true // Define o login como padrão
    }

    private fun showMainScreen() {
        authLayout.visibility = View.GONE
        mainLayout.visibility = View.VISIBLE
        tvWelcome.text = "Bem-vindo, $currentUsername!"
        // Esconde todas as seções de ação ao entrar na tela principal
        hideAllActionSections()
    }

    private fun hideAllActionSections() {
        addValueSection.visibility = View.GONE
        viewDataSection.visibility = View.GONE
        sumTotalSection.visibility = View.GONE
        clearDataSection.visibility = View.GONE
    }

    private fun showActionSection(section: View) {
        hideAllActionSections()
        section.visibility = View.VISIBLE
    }

    // Função para criptografar senha (SHA-256)
    private fun hashPassword(password: String): String {
        try {
            val digest = java.security.MessageDigest.getInstance("SHA-256")
            val hash = digest.digest(password.toByteArray(StandardCharsets.UTF_8))
            val hexString = StringBuilder()
            for (b in hash) {
                val hex = Integer.toHexString(0xff and b.toInt())
                if (hex.length == 1) hexString.append('0')
                hexString.append(hex)
            }
            return hexString.toString()
        } catch (e: NoSuchAlgorithmException) {
            Log.e("Hashing", "Erro ao criptografar senha", e)
            return "" // Em caso de erro, retorna vazio (ou lança exceção)
        }
    }

    // Carrega os dados do usuário do SharedPreferences
    private fun loadUserData(username: String): UserData {
        val json = sharedPreferences.getString("user_data_$username", null)
        return if (json != null) {
            gson.fromJson(json, object : TypeToken<UserData>() {}.type)
        } else {
            UserData("", mutableListOf()) // Retorna um objeto vazio se não houver dados
        }
    }

    // Salva os dados do usuário no SharedPreferences
    private fun saveUserData(username: String, data: UserData) {
        val json = gson.toJson(data)
        sharedPreferences.edit().putString("user_data_$username", json).apply()
        currentUserData = data // Atualiza o estado local
    }

    // Lida com o login e cadastro
    private fun handleAuth() {
        val username = etUsernameAuth.text.toString().trim()
        val password = etPasswordAuth.text.toString().trim()

        if (username.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Por favor, preencha usuário e senha.", Toast.LENGTH_SHORT).show()
            return
        }

        val hashedPassword = hashPassword(password)
        val storedUserData = loadUserData(username)
        val isRegisterAction = rgAction.checkedRadioButtonId == R.id.rb_register

        if (isRegisterAction) {
            if (storedUserData.passwordHash.isNotEmpty()) { // Usuário já existe e tem senha
                Toast.makeText(this, "Usuário já existe.", Toast.LENGTH_SHORT).show()
            } else {
                val newUserData = UserData(hashedPassword, mutableListOf())
                saveUserData(username, newUserData)
                Toast.makeText(this, "Cadastro realizado com sucesso!", Toast.LENGTH_SHORT).show()
                rbLogin.isChecked = true // Mudar para login após o cadastro
            }
        } else { // Ação de Login
            if (storedUserData.passwordHash.isEmpty()) { // Usuário não existe ou não tem senha
                Toast.makeText(this, "Usuário não encontrado ou não cadastrado.", Toast.LENGTH_SHORT).show()
                return
            }
            if (storedUserData.passwordHash == hashedPassword) {
                currentUsername = username
                currentUserData = storedUserData
                Toast.makeText(this, "Bem-vindo, $username!", Toast.LENGTH_SHORT).show()
                showMainScreen()
            } else {
                Toast.makeText(this, "Senha incorreta.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    // Adiciona um novo valor
    private fun addValue() {
        val valueStr = etNewValue.text.toString().trim()
        if (valueStr.isEmpty()) {
            Toast.makeText(this, "Por favor, digite um valor.", Toast.LENGTH_SHORT).show()
            return
        }
        val value = valueStr.toDoubleOrNull()
        if (value == null) {
            Toast.makeText(this, "Valor inválido. Digite um número.", Toast.LENGTH_SHORT).show()
            return
        }

        currentUserData.values.add(value)
        saveUserData(currentUsername, currentUserData)
        etNewValue.setText("")
        Toast.makeText(this, "Valor $value adicionado com sucesso!", Toast.LENGTH_SHORT).show()
    }

    // Exibe todos os valores armazenados
    private fun displayStoredValues() {
        if (currentUserData.values.isEmpty()) {
            tvStoredValues.text = "Nenhum valor armazenado ainda."
        } else {
            tvStoredValues.text = currentUserData.values.joinToString("\n") { "- ${it.toString()}" }
        }
    }

    // Exibe a soma total dos valores
    private fun displayTotalSum() {
        val total = currentUserData.values.sum()
        tvTotalSum.text = "Soma Total: ${total.toString()}"
    }

    // Confirma e limpa os dados
    private fun confirmClearData() {
        AlertDialog.Builder(this)
            .setTitle("Confirmar Limpeza")
            .setMessage("Tem certeza que deseja limpar todos os dados?")
            .setPositiveButton("Limpar") { dialog, _ ->
                currentUserData.values.clear()
                saveUserData(currentUsername, currentUserData)
                Toast.makeText(this, "Todos os dados foram removidos.", Toast.LENGTH_SHORT).show()
                dialog.dismiss()
            }
            .setNegativeButton("Cancelar") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
}

// Classe de dados para armazenar as informações do usuário
data class UserData(
    var passwordHash: String,
    val values: MutableList<Double>
)
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="[http://schemas.android.com/apk/res/android](http://schemas.android.com/apk/res/android)"
    xmlns:app="[http://schemas.android.com/apk/res-auto](http://schemas.android.com/apk/res-auto)"
    xmlns:tools="[http://schemas.android.com/tools](http://schemas.android.com/tools)"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp"
    android:background="#F0F2F5"
    tools:context=".MainActivity">

    <TextView
        android:id="@+id/app_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="🤖 LZTech Chatbot"
        android:textSize="28sp"
        android:textStyle="bold"
        android:textColor="#333"
        android:gravity="center"
        android:layout_marginBottom="5dp" />

    <TextView
        android:id="@+id/tv_date"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="📅 Data: DD/MM/AAAA"
        android:textSize="16sp"
        android:textColor="#666"
        android:gravity="center"
        android:layout_marginBottom="20dp" />

    <LinearLayout
        android:id="@+id/auth_layout"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="20dp"
        android:background="@drawable/rounded_card_background"
        android:elevation="5dp"
        android:layout_gravity="center">

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="🔐 Login ou Cadastro"
            android:textSize="22sp"
            android:textStyle="bold"
            android:textColor="#444"
            android:gravity="center"
            android:layout_marginBottom="20dp" />

        <EditText
            android:id="@+id/et_username_auth"
            android:layout_width="match_parent"
            android:layout_height="50dp"
            android:hint="Usuário"
            android:inputType="text"
            android:paddingStart="15dp"
            android:paddingEnd="15dp"
            android:background="@drawable/edittext_background"
            android:layout_marginBottom="15dp"
            android:textSize="16sp" />

        <EditText
            android:id="@+id/et_password_auth"
            android:layout_width="match_parent"
            android:layout_height="50dp"
            android:hint="Senha"
            android:inputType="textPassword"
            android:paddingStart="15dp"
            android:paddingEnd="15dp"
            android:background="@drawable/edittext_background"
            android:layout_marginBottom="20dp"
            android:textSize="16sp" />

        <RadioGroup
            android:id="@+id/rg_action"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center"
            android:layout_marginBottom="20dp">

            <RadioButton
                android:id="@+id/rb_login"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Login"
                android:checked="true"
                android:buttonTint="#007bff"
                android:textColor="#007bff"
                android:textStyle="bold"
                android:layout_marginEnd="20dp" />

            <RadioButton
                android:id="@+id/rb_register"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Cadastrar"
                android:buttonTint="#007bff"
                android:textColor="#007bff"
                android:textStyle="bold" />
        </RadioGroup>

        <Button
            android:id="@+id/btn_auth"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Login"
            android:background="@drawable/button_background"
            android:textColor="@android:color/white"
            android:padding="12dp"
            android:textSize="18sp"
            android:textStyle="bold" />

    </LinearLayout>

    <LinearLayout
        android:id="@+id/main_layout"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:padding="20dp"
        android:background="@drawable/rounded_card_background"
        android:elevation="5dp"
        android:visibility="gone"> <TextView
            android:id="@+id/tv_welcome"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Bem-vindo, Usuário!"
            android:textSize="24sp"
            android:textStyle="bold"
            android:textColor="#333"
            android:gravity="center"
            android:layout_marginBottom="20dp" />

        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Ações disponíveis:"
            android:textSize="20sp"
            android:textStyle="bold"
            android:textColor="#555"
            android:layout_marginBottom="10dp"
            android:paddingBottom="5dp"
            android:background="@drawable/bottom_border_background" />

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_horizontal"
            android:layout_marginBottom="20dp"
            android:flexWrap="wrap"> <Button
                android:id="@+id/btn_add_value"
                style="@style/ActionButtonStyle"
                android:text="➕ Adicionar valor" />

            <Button
                android:id="@+id/btn_view_data"
                style="@style/ActionButtonStyle"
                android:text="📊 Ver todos os dados" />

            <Button
                android:id="@+id/btn_sum_total"
                style="@style/ActionButtonStyle"
                android:text="➗ Ver a soma total" />

            <Button
                android:id="@+id/btn_clear_data"
                style="@style/ActionButtonStyle"
                android:text="🧹 Limpar dados" />
        </LinearLayout>

        <LinearLayout
            android:id="@+id/add_value_section"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="15dp"
            android:background="@drawable/section_background"
            android:layout_marginBottom="20dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Adicionar valor:"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="#495057"
                android:layout_marginBottom="10dp" />

            <EditText
                android:id="@+id/et_new_value"
                android:layout_width="match_parent"
                android:layout_height="50dp"
                android:hint="Digite um valor numérico"
                android:inputType="numberDecimal"
                android:paddingStart="15dp"
                android:paddingEnd="15dp"
                android:background="@drawable/edittext_background"
                android:layout_marginBottom="15dp"
                android:textSize="16sp" />

            <Button
                android:id="@+id/btn_confirm_add_value"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Adicionar"
                android:background="@drawable/button_background"
                android:textColor="@android:color/white"
                android:padding="12dp"
                android:textSize="16sp"
                android:textStyle="bold" />
        </LinearLayout>

        <LinearLayout
            android:id="@+id/view_data_section"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="15dp"
            android:background="@drawable/section_background"
            android:layout_marginBottom="20dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Valores armazenados:"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="#495057"
                android:layout_marginBottom="10dp" />

            <ScrollView
                android:layout_width="match_parent"
                android:layout_height="wrap_content">
                <TextView
                    android:id="@+id/tv_stored_values"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:text="Nenhum valor armazenado ainda."
                    android:textSize="16sp"
                    android:textColor="#343a40"
                    android:padding="5dp" />
            </ScrollView>
        </LinearLayout>

        <LinearLayout
            android:id="@+id/sum_total_section"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="15dp"
            android:background="@drawable/section_background"
            android:layout_marginBottom="20dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Soma total dos dados:"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="#495057"
                android:layout_marginBottom="10dp" />

            <TextView
                android:id="@+id/tv_total_sum"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="0.0"
                android:textSize="28sp"
                android:textStyle="bold"
                android:textColor="#007bff"
                android:gravity="center"
                android:paddingVertical="10dp" />
        </LinearLayout>

        <LinearLayout
            android:id="@+id/clear_data_section"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="15dp"
            android:background="@drawable/section_background"
            android:layout_marginBottom="20dp"
            android:visibility="gone">

            <TextView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Limpar dados:"
                android:textSize="18sp"
                android:textStyle="bold"
                android:textColor="#495057"
                android:layout_marginBottom="10dp" />

            <Button
                android:id="@+id/btn_confirm_clear_data"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:text="Confirmar limpeza dos dados"
                android:background="@drawable/button_red_background"
                android:textColor="@android:color/white"
                android:padding="12dp"
                android:textSize="16sp"
                android:textStyle="bold" />
        </LinearLayout>

        <Button
            android:id="@+id/btn_logout"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Sair"
            android:background="@drawable/button_secondary_background"
            android:textColor="@android:color/white"
            android:padding="12dp"
            android:textSize="18sp"
            android:textStyle="bold"
            android:layout_marginTop="20dp" />

    </LinearLayout>

</LinearLayout>
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="@android:color/white"/>
    <corners android:radius="10dp"/>
</shape>
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="[http://schemas.android.com/apk/res/android](http://schemas.android.com/apk/res/android)">
    <solid android:color="#F9F9F9"/>
    <stroke android:color="#CCCCCC" android:width="1dp"/>
    <corners android:radius="8dp"/>
</shape>
```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_pressed="true">
        <shape>
            <solid android:color="#0056b3"/> <corners android:radius="8dp"/>
        </shape>
    </item>
    <item>
        <shape>
            <solid android:color="#007bff"/> <corners android:radius="8dp"/>
        </shape>
    </item>
</selector>
```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="[http://schemas.android.com/apk/res/android](http://schemas.android.com/apk/res/android)">
    <item android:state_pressed="true">
        <shape>
            <solid android:color="#c82333"/> <corners android:radius="8dp"/>
        </shape>
    </item>
    <item>
        <shape>
            <solid android:color="#dc3545"/> <corners android:radius="8dp"/>
        </shape>
    </item>
</selector>
```xml
<?xml version="1.0" encoding="utf-8"?>
<selector xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:state_pressed="true">
        <shape>
            <solid android:color="#545b62"/> <corners android:radius="8dp"/>
        </shape>
    </item>
    <item>
        <shape>
            <solid android:color="#6c757d"/> <corners android:radius="8dp"/>
        </shape>
    </item>
</selector>
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="[http://schemas.android.com/apk/res/android](http://schemas.android.com/apk/res/android)">
    <solid android:color="#F8F9FA"/>
    <stroke android:color="#E2E6EA" android:width="1dp"/>
    <corners android:radius="8dp"/>
</shape>
```xml
<?xml version="1.0" encoding="utf-8"?>
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:top="-2dp" android:right="-2dp" android:left="-2dp">
        <shape>
            <solid android:color="@android:color/transparent" />
            <stroke android:width="1dp" android:color="#EEE" />
        </shape>
    </item>
</layer-list>
```xml
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.DarkActionBar">
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryDark">@color/purple_700</item>
        <item name="colorAccent">@color/teal_200</item>
    </style>

    <style name="ActionButtonStyle">
        <item name="android:layout_width">wrap_content</item>
        <item name="android:layout_height">wrap_content</item>
        <item name="android:background">@drawable/button_secondary_background</item>
        <item name="android:textColor">@android:color/white</item>
        <item name="android:padding">12dp</item>
        <item name="android:textSize">14sp</item>
        <item name="android:textStyle">bold</item>
        <item name="android:layout_margin">5dp</item>
        <item name="android:elevation">3dp</item>
    </style>
</resources>
