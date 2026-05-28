package com.example.luxmind_mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

data class LoginRequest(val username: String, val password: String)
data class LoginResponse(val token: String, val id: Int, val role: String)
data class BrightnessRequest(val current_brightness: Int) // НОВЕ: для оновлення яскравості

data class PaginatedResponse<T>(val results: List<T>)

data class Dashboard(val id: Int, val name: String)
data class Zone(val id: Int, val name: String, val type: String)
data class Lamp(val id: Int, val serial_number: String, val current_brightness: Int, val status: String)

interface LuxMindApi {
    @POST("api/v1/login/")
    suspend fun login(@Body req: LoginRequest): LoginResponse

    @GET("api/v1/dashboards/")
    suspend fun getDashboards(@Query("id") userId: Int): PaginatedResponse<Dashboard>

    @GET("api/v1/zones/")
    suspend fun getZones(@Query("id") dashboardId: Int): PaginatedResponse<Zone>

    @GET("api/v1/lamps/")
    suspend fun getLamps(@Query("id") zoneId: Int): PaginatedResponse<Lamp>

    @PATCH("api/v1/lamps/{id}/")
    suspend fun updateBrightness(@Path("id") lampId: Int, @Body req: BrightnessRequest): Lamp
}

object RetrofitClient {
    private const val BASE_URL = "https://luxmind-api.onrender.com/"

    val api: LuxMindApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(LuxMindApi::class.java)
    }
}

class LuxMindViewModel : ViewModel() {
    var userId by mutableStateOf<Int?>(null)
    var errorMsg by mutableStateOf("")
    var successMsg by mutableStateOf("") // НОВЕ: Сповіщення про успіх

    var dashboards by mutableStateOf<List<Dashboard>>(emptyList())
    var zones by mutableStateOf<List<Zone>>(emptyList())
    var lamps by mutableStateOf<List<Lamp>>(emptyList())

    var selectedDashboard by mutableStateOf<Dashboard?>(null)
    var selectedZone by mutableStateOf<Zone?>(null)

    fun login(user: String, pass: String) {
        viewModelScope.launch {
            try {
                val response = RetrofitClient.api.login(LoginRequest(user, pass))
                if (response.role == "operator" || response.role == "admin") {
                    userId = response.id
                    loadDashboards(response.id)
                } else {
                    errorMsg = "Доступ дозволено лише операторам!"
                }
            } catch (e: Exception) {
                errorMsg = "Помилка входу: Перевірте дані"
            }
        }
    }

    private suspend fun loadDashboards(id: Int) {
        try {
            dashboards = RetrofitClient.api.getDashboards(id).results
        } catch (e: Exception) { errorMsg = "Помилка завантаження дашбордів" }
    }

    fun selectDashboard(db: Dashboard) {
        selectedDashboard = db
        selectedZone = null
        lamps = emptyList()
        successMsg = ""
        viewModelScope.launch {
            try {
                zones = RetrofitClient.api.getZones(db.id).results
            } catch (e: Exception) { errorMsg = "Помилка завантаження зон" }
        }
    }

    fun selectZone(zone: Zone) {
        selectedZone = zone
        successMsg = ""
        viewModelScope.launch {
            try {
                lamps = RetrofitClient.api.getLamps(zone.id).results
            } catch (e: Exception) { errorMsg = "Помилка завантаження світильників" }
        }
    }

    fun updateLampBrightness(lampId: Int, newBrightness: Int) {
        viewModelScope.launch {
            try {
                val updatedLamp = RetrofitClient.api.updateBrightness(lampId, BrightnessRequest(newBrightness))
                // Оновлюємо локальний список, щоб UI миттєво змінився
                lamps = lamps.map { if (it.id == lampId) updatedLamp else it }
                successMsg = "Яскравість успішно оновлено!"
            } catch (e: Exception) {
                errorMsg = "Помилка оновлення яскравості"
            }
        }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    val viewModel: LuxMindViewModel = viewModel()
                    if (viewModel.userId == null) {
                        LoginScreen(viewModel)
                    } else {
                        OperatorScreen(viewModel)
                    }
                }
            }
        }
    }
}

@Composable
fun LoginScreen(viewModel: LuxMindViewModel) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text("LuxMind Operator", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = Color(0xFF0D47A1))
        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(value = username, onValueChange = { username = it }, label = { Text("Логін") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(value = password, onValueChange = { password = it }, label = { Text("Пароль") }, modifier = Modifier.fillMaxWidth())
        Spacer(modifier = Modifier.height(16.dp))

        if (viewModel.errorMsg.isNotEmpty()) {
            Text(viewModel.errorMsg, color = Color.Red)
            Spacer(modifier = Modifier.height(8.dp))
        }

        Button(onClick = { viewModel.login(username, password) }, modifier = Modifier.fillMaxWidth()) {
            Text("Увійти в систему")
        }
    }
}

@Composable
fun OperatorScreen(viewModel: LuxMindViewModel) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Дашборди", fontWeight = FontWeight.Bold, fontSize = 18.sp)
        Row {
            viewModel.dashboards.forEach { db ->
                Button(
                    onClick = { viewModel.selectDashboard(db) },
                    modifier = Modifier.padding(end = 8.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (viewModel.selectedDashboard == db) Color(0xFF0D47A1) else Color.Gray
                    )
                ) { Text(db.name) }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (viewModel.selectedDashboard != null) {
            Text("Зони", fontWeight = FontWeight.Bold, fontSize = 18.sp)
            Row {
                viewModel.zones.forEach { zone ->
                    Button(
                        onClick = { viewModel.selectZone(zone) },
                        modifier = Modifier.padding(end = 8.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (viewModel.selectedZone == zone) Color(0xFF1976D2) else Color.Gray
                        )
                    ) { Text(zone.name) }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (viewModel.successMsg.isNotEmpty()) {
            Text(viewModel.successMsg, color = Color(0xFF388E3C), fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
        }

        if (viewModel.selectedZone != null) {
            val total = viewModel.lamps.size
            val active = viewModel.lamps.count { it.status == "active" }
            val faulty = viewModel.lamps.count { it.status == "faulty" }
            val inactive = viewModel.lamps.count { it.status == "inactive" }

            Card(modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp)) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Аналітика зони", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                    Text("Всього світильників: $total")
                    Text("🟢 Активні: $active", color = Color(0xFF388E3C))
                    Text("⚪ Неактивні: $inactive", color = Color.Gray)
                    Text("🔴 Зламані: $faulty", color = Color.Red)
                }
            }

            LazyColumn {
                items(viewModel.lamps) { lamp ->
                    LampItemCard(lamp = lamp, viewModel = viewModel)
                }
            }
        }
    }
}

@Composable
fun LampItemCard(lamp: Lamp, viewModel: LuxMindViewModel) {
    var sliderValue by remember(lamp.current_brightness) { mutableStateOf(lamp.current_brightness.toFloat()) }

    val isFaulty = lamp.status == "faulty"

    Card(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("SN: ${lamp.serial_number}", fontWeight = FontWeight.Bold)

                val statusColor = when(lamp.status) {
                    "active" -> Color(0xFF388E3C)
                    "faulty" -> Color.Red
                    else -> Color.Gray
                }
                Text(lamp.status.uppercase(), color = statusColor, fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(8.dp))

            if (!isFaulty) {
                Text("Яскравість: ${sliderValue.toInt()}%")
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Slider(
                        value = sliderValue,
                        onValueChange = { sliderValue = it },
                        valueRange = 0f..100f,
                        modifier = Modifier.weight(1f)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(onClick = { viewModel.updateLampBrightness(lamp.id, sliderValue.toInt()) }) {
                        Text("Зберегти")
                    }
                }
            } else {
                Text("Яскравість: ${lamp.current_brightness}% (Заблоковано, потребує ремонту)", color = Color.Red)
            }
        }
    }
}